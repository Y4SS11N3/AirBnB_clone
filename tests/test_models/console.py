#!/usr/bin/python3
"""
This is the entry point of the command interpreter.
Authors: YASSINE - ANAS
"""
import cmd
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review
import re
import ast


class HBNBCommand(cmd.Cmd):
    prompt = '(hbnb) '
    classes = {
        "BaseModel": BaseModel,
        "User": User,
        "Place": Place,
        "State": State,
        "City": City,
        "Amenity": Amenity,
        "Review": Review
    }

    def do_quit(self, arg):
        """Exits the console. Usage: quit"""
        return True

    def do_EOF(self, arg):
        """Exits console with EOF (Ctrl+D)."""
        print("")
        return True

    def emptyline(self):
        """Does nothing on empty input."""
        pass

    def do_create(self, arg):
        """
        Creates a new instance of BaseModel. Usage: create <class name>
        Example: create User
        """
        args = arg.split()
        if not args:
            print("** class name missing **")
            return
        if '.' in args[0]:
            print("*** Unknown syntax: {} ***".format(arg))
            return
        if args[0] not in self.classes:
            print("** class doesn't exist **")
            return
        instance = self.classes[args[0]]()
        instance.save()
        print(instance.id)

    def do_show(self, arg):
        """
        Shows an instance based on the class name and id.
        Usage: show <class name> <id>
        Example: show User 1234-1234-1234
        """
        args = arg.split()
        if not args:
            print("** class name missing **")
            return
        if args[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(args) < 2:
            print("** instance id missing **")
            return
        key = "{}.{}".format(args[0], args[1])
        if key not in storage.all():
            print("** no instance found **")
        else:
            print(storage.all()[key])

    def do_destroy(self, arg):
        """
        Deletes an instance based on the class name and id.
        Usage: destroy <class name> <id>
        Example: destroy User 1234-1234-1234
        """
        args = arg.split()
        if len(args) == 0:
            print("** class doesn't exist **")
        elif args[0] not in self.classes:
            print("** class doesn't exist **")
        elif len(args) == 1:
            print("** instance id missing **")
        else:
            key = f"{args[0]}.{args[1]}"
            if key not in storage.all():
                print("** no instance found **")
            else:
                del storage.all()[key]
                storage.save()

    def do_all(self, arg):
        """
        Shows all instances of a class or all classes if not specified.
        Usage: all or all <class name>
        Example: all User
        """
        args = arg.split()
        instances = storage.all()
        if not args:
            print([str(v) for v in instances.values()])
        elif args[0] in self.classes:
            filtered_instances = [
                str(v) for v in instances.values()
                if type(v).__name__ == args[0]
            ]
            print(filtered_instances)
        else:
            print("** class doesn't exist **")

    def do_update(self, arg):
        """
        Updates an instance by adding or updating attribute.
        Usage: update <class name> <id> <attribute name> "<attribute value>"
        Example: update User 1234-1234-1234 email "contact@yassine.fun"
        """
        args = arg.split(" ", 3)
        if not args or args[0] == "":
            print("** class name missing **")
            return
        if args[0] not in self.classes:
            print("** class doesn't exist **")
            return
        if len(args) < 2 or args[1] == "":
            print("** instance id missing **")
            return
        key = "{}.{}".format(args[0], args[1])
        if key not in storage.all():
            print("** no instance found **")
            return
        if len(args) < 3 or args[2] == "":
            print("** attribute name missing **")
            return
        if len(args) < 4:
            print("** value missing **")
            return
        obj = storage.all()[key]
        try:
            attr_value = ast.literal_eval(args[3])
        except (ValueError, SyntaxError):
            attr_value = args[3].strip("\"")
        setattr(obj, args[2], attr_value)
        obj.save()

    def do_count(self, arg):
        """
        Counts instances of a specific class.
        Usage: count <class name>
        Example: count User
        """
        args = arg.split()
        if len(args) != 1:
            print("** class name missing or too many args **")
            return
        class_name = args[0]
        if class_name not in self.classes:
            print("** class doesn't exist **")
            return
        count = 0
        for obj_id in storage.all():
            if obj_id.startswith(class_name + "."):
                count += 1
        print(count)

    def default(self, line):
        """Handles unrecognized commands. Shows syntax error."""
        if ".create()" in line:
            print("*** Unknown syntax: {}".format(line))
            return

        try:
            cls_name, command, arguments = self.parse_line(line)
            if cls_name not in self.classes:
                print("** class doesn't exist **")
                return

            arguments_clean = arguments.replace('\"', '')
            args_list = arguments_clean.split(',')

            if command in ["show", "destroy"]:
                command_func = getattr(self, f'do_{command}', None)
                if command_func:
                    command_func(f"{cls_name} {' '.join(args_list)}")
            elif command == "count":
                self.do_count(cls_name)
            elif command in ["all", "create", "update"]:
                self.onecmd(f"{command} {cls_name} {' '.join(args_list)}")
            else:
                print(f"*** Unknown syntax: {line} ***")
        except ValueError:
            print("** class doesn't exist **")

    def parse_line(self, line):
        """Parses input to retrieve class name, command, and arguments."""
        pattern = re.compile(r"^(\w+)\.(\w+)\((.*)\)$")
        match = pattern.match(line)
        if match:
            cls_name, command, arguments = match.groups()
            return cls_name, command, arguments
        else:
            raise ValueError("Invalid command syntax")

    def handle_update(self, cls_name, arguments):
        """Handles update action for dictionary updates."""
        if "{" in arguments and "}" in arguments:
            id_arg, dict_arg = arguments.split(",", 1)
            dict_arg = ast.literal_eval(dict_arg.strip())
            for key, value in dict_arg.items():
                self.do_update(
                    "{} {} {} \"{}\"".format(
                        cls_name, id_arg.strip("\""), key, value
                    )
                )
        else:
            args = arguments.split(",", 2)
            if len(args) == 3:
                id_arg, key_arg, value_arg = args
                self.do_update(
                    "{} {} {} {}".format(
                        cls_name, id_arg.strip("\""),
                        key_arg.strip(), value_arg.strip()
                    )
                )
            else:
                print("** Invalid arguments **")

    def count_instances(self, class_name):
        """Counts the number of instances for a given class name."""
        count = sum(
            1 for obj in storage.all().values()
            if obj.__class__.__name__ == class_name
        )
        print(count)


if __name__ == '__main__':
    HBNBCommand().cmdloop()

