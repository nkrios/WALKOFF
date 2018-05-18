import json
import os


def convert_playbooks():
    for subd, d, files in os.walk('./tests/testWorkflows'):
        for f in files:
            if f.endswith('.playbook'):
                path = os.path.join(subd, f)
                with open(path, 'r') as playbook_file:
                    print(playbook_file)
                    playbook = convert_playbook(json.load(playbook_file))
                with open(path, 'w') as playbook_file:
                    #print(playbook)
                    playbook_file.write(json.dumps(playbook, sort_keys=True, indent=4, separators=(',', ': ')))


def convert_playbook(playbook):
    for workflow in playbook.get('workflows', []):
        convert_workflow(workflow)
    return playbook


def convert_workflow(workflow):
    convert_subelements(workflow, 'actions', convert_action)
    convert_subelements(workflow, 'branches', convert_branch)


def convert_subelements(root, element_name, converter):
    for element in root.get(element_name, []):
        converter(element)


def convert_action(action):
    pass


def convert_branch(branch):
    branch['destination_type'] = 'action'

if __name__ == '__main__':
    convert_playbooks()
