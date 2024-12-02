import sys
import xml.etree.ElementTree as ET

def usage():
    print("Usage: python keymap.py <gold> <updated>")

def main():
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    gold_xml = ET.parse(sys.argv[1])
    updated_xml = ET.parse(sys.argv[2])

    gold_keymap = gold_xml.getroot()
    updated_keymap = updated_xml.getroot()

    gold_enabled_actions = []
    gold_disabled_actions = []
    for action in gold_keymap.findall('action'):
        if action.find('keyboard-shortcut') is not None:
            gold_enabled_actions.append(action)
        else:
            gold_disabled_actions.append(action)

    updated_enabled_actions = {}
    updated_disabled_actions = []
    for action in updated_keymap.findall('action'):
        if action.find('keyboard-shortcut') is not None:
            updated_enabled_actions[action.attrib['id']] = action
        else:
            updated_disabled_actions.append(action)
    udpated_disabled_ids = { o.attrib['id'] for o in gold_disabled_actions}

    if updated_keymap.attrib['parent'] == gold_keymap.attrib['name']:
        print('<keymap version="%s" name="%s" parent="%s">' % (gold_keymap.attrib['version'], gold_keymap.attrib['name'], gold_keymap.attrib['parent']))

        printed_ids = set()
        # print gold enabled unless they are disabled in update, if they are updated, print updated version
        for action in gold_enabled_actions:
            action_id = action.attrib['id']
            if action_id in udpated_disabled_ids:
                continue
            elif updated_enabled_actions.get(action_id, None) is not None:
                print("  %s" % ET.tostring(updated_enabled_actions.get(action_id), encoding='unicode').rstrip(' \n'))
            else:
                print("  %s" % ET.tostring(action, encoding='unicode').rstrip(' \n'))
            printed_ids.add(action_id)

        # print updated enabled
        for action in updated_enabled_actions.values():
            if action.attrib['id'] not in printed_ids:
                print("  %s" % ET.tostring(action, encoding='unicode').rstrip(' \n'))
                printed_ids.add(action.attrib['id'])

        # join gold disabled - updated enabled and updated disabled and print them
        all_disabled = []
        all_disabled_ids = set()
        for action in gold_disabled_actions:
            action_id = action.attrib['id']
            if action_id not in printed_ids and action_id not in all_disabled_ids:
                all_disabled.append(action)
                all_disabled_ids.add(action_id)
        for action in updated_disabled_actions:
            action_id = action.attrib['id']
            if action_id not in printed_ids and action_id not in all_disabled_ids:
                all_disabled.append(action)
                all_disabled_ids.add(action_id)

        all_disabled.sort(key=lambda x: x.attrib['id'])
        print("\n  <!-- disabled actions -->")
        for o in all_disabled:
            print("  %s" % ET.tostring(o, encoding='unicode').rstrip(' \n'))

        print("</keymap>")

    else:
        print('<keymap version="%s" name="%s" parent="%s">' % (gold_keymap.attrib['version'], gold_keymap.attrib['name'], gold_keymap.attrib['parent']))

        # print gold actions preserving the order
        for action in gold_enabled_actions:
            action = updated_enabled_actions.pop(action.attrib['id'], None)
            if action is not None:
                print("  %s" % ET.tostring(action, encoding='unicode').rstrip(' \n'))
            else:
                pass

        # added enabled actions
        if updated_enabled_actions:
            print("\n  <!-- added actions -->")
            for o in updated_enabled_actions.values():
                print("  %s" % ET.tostring(o, encoding='unicode').rstrip(' \n'))

        updated_disabled_actions.sort(key=lambda x: x.attrib['id'])
        print("\n  <!-- disabled actions -->")
        for o in updated_disabled_actions:
            print("  %s" % ET.tostring(o, encoding='unicode').rstrip(' \n'))

        print("</keymap>")


if __name__ == '__main__':
    main()
