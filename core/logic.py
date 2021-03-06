from core import locale_manager
from schedule.exceptions import NoSchedule
from schedule.api import get_schedule
from schedule.prettify import prettify_schedule
from schedule.tools import get_today_schedule, get_tomorrow_schedule
from model.chat import Chat


def help_command(command, explanation, template):
    return template.format(
        command=command,
        explanation=explanation,
    )


def has_triggered_command(command_list, message):
    for phrase in command_list:
        if message.startswith(phrase.lower()):
            return phrase


def parse_message(command_list, message):
    for command in command_list.keys():
        triggered_phrase = has_triggered_command(command_list[command]["commands"], message)
        if triggered_phrase:
            return command, message.split(triggered_phrase.lower())[1]
    return None, None


def perform_command(command: str, params: str, reply, locale):
    try:
        chat_id = str(reply.get_chat_id())
        if command == "get_current_schedule":
            if len(params) == 0:
                chat = Chat.get_chat_by_chat_id(chat_id)
                if chat:
                    schedule = get_schedule(chat.group_id)
                else:
                    reply.send_text(locale['chat_is_not_registered'])
                    return
            else:
                schedule = get_schedule(params[0])
            reply.send_text(get_prettified_schedule(locale, schedule, get_today_schedule))

        if command == "get_tomorrow_schedule":
            chat = Chat.get_chat_by_chat_id(chat_id)
            if chat:
                schedule = get_schedule(chat.group_id)
            else:
                reply.send_text(locale['chat_is_not_registered'])
                return
            reply.send_text(get_prettified_schedule(locale, schedule, get_tomorrow_schedule))

        if command == "building_info":
            if len(params) == 0:
                reply.send_text(locale['building_not_found'])
            else:
                try:
                    buildings = locale_manager.read_buildings(locale)
                    looking_for_building = ''.join(filter(lambda x: x.isdigit(), params[0]))
                    reply.send_text(buildings[looking_for_building])
                except KeyError:
                    reply.send_text(locale['building_not_found'])

        if command == "absent":
            is_done = Chat.add_student(chat_id,
                                       reply.get_message_author_name(),
                                       reply.get_message_author(),
                                       reason=params)
            if is_done:
                reply.send_text(locale['done_absent'])
            else:
                reply.send_text(locale['cant_absent'])

        if command == "deabsent":
            is_done = Chat.remove_student(chat_id, reply.get_message_author())
            if is_done:
                reply.send_text(locale['done_deabsent'])
            else:
                reply.send_text(locale['didnt_deabsent'])

        if command == "absent_list":
            resp_list, date = Chat.generate_list(chat_id,
                                                 locale['default_list_content'],
                                                 locale['row_template'])
            if resp_list:
                reply.send_text(locale['list_template'].format(
                    date=date,
                    content=resp_list
                ))
            else:
                reply.send_text(locale['cant_make_list'])

        if command == "register_chat":
            group_id = params.strip()

            if Chat.register_chat(chat_id, group_id):
                reply.send_text(locale['registered'].format(group_id=group_id))
            else:
                reply.send_text(locale['group_has_changed'].format(group_id=group_id))

        if command == "help":
            content = '\n'.join(map(lambda command:
                                    help_command(locale["commands"][command]["commands"][0],
                                                 locale["commands"][command]["explanation"],
                                                 locale["row_help_template"]),
                                    locale["commands"].keys()))
            reply.send_text(locale['help_message'].format(
                help_message=content
            ))

    except NoSchedule:
        reply.send_text(locale['group_not_found'])


def get_prettified_schedule(locale, schedule, selector):
    lesson_template = locale_manager.read_lesson_template(locale)
    subgroup_template = locale_manager.read_subgroup_template(locale)
    lesson_types = locale_manager.read_lesson_types(locale)
    nothing = locale_manager.read_nothing(locale)
    schedule = selector(schedule)

    return prettify_schedule(schedule,
                             lesson_template,
                             lesson_types,
                             subgroup_template,
                             nothing)


def on_message(reply, message_text):
    locale = locale_manager.read_locale()
    if message_text.startswith(locale_manager.read_prefix(locale)):
        # We should remove prefix
        lowered_message = message_text.lower()[1:]
        command, params = parse_message(locale['commands'], lowered_message)
        if command:
            perform_command(command, params, reply, locale)
