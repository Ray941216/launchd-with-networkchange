#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author: JeffMa
# @migrate-to-python3: RayChen

import sys
import os
import time
import subprocess
import getpass


# current dir
dir_path = os.path.dirname(os.path.abspath(__file__))


def add_to_keychain(username, password):
    p = subprocess.Popen(
        [
            "/usr/bin/security",
            "add-generic-password",
            "-a",
            username,
            "-s",
            "launchd with networkchange",
            "-w",
            password,
            "-T",
            "",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.communicate()
    if p.returncode != 0:
        return False
    return True


def delete_from_keychain(username):
    p = subprocess.Popen(
        [
            "/usr/bin/security",
            "delete-generic-password",
            "-a",
            username,
            "-s",
            "launchd with networkchange",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.communicate()
    if p.returncode != 0:
        return False
    return True


def script_header():
    print(
        "----------------\n"
        "launchd with networkchange\n"
        "see: https://github.com/Jeff2Ma/launchd-with-networkchange for more help.\n"
        "by JeffMa v1.2\n"
        "----------------"
    )


def script_footer():
    print("All done! Please edit the codes in `example.sh` as what you want.")


def create_plist_file():
    appscript_file_path = os.path.join(dir_path, "run.applescript")
    stdout_log = os.path.join(dir_path, "onnetworkchange.log")
    stderr_log = os.path.join(dir_path, "onnetworkchange.err.log")
    file_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n'
        "<dict>\n"
        "\t<key>Label</key>\n"
        "\t<string>com.devework.onnetworkchange</string>\n"
        "\t<key>ProgramArguments</key>\n"
        "\t<array>\n"
        "\t\t<string>/usr/bin/osascript</string>\n"
        f"\t\t<string>{appscript_file_path}</string>\n"
        "\t</array>\n"
        "\t<key>StandardOutPath</key>\n"
        f"\t<string>{stdout_log}</string>\n"
        "\t<key>StandardErrorPath</key>\n"
        f"\t<string>{stderr_log}</string>\n"
        "\t<key>WatchPaths</key>\n"
        "\t<array>\n"
        "\t\t<string>/Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist</string>\n"
        "\t\t<string>/Library/Preferences/SystemConfiguration/com.apple.wifi.message-tracer.plist</string>\n"
        "\t</array>\n"
        "</dict>\n"
        "</plist>"
    )

    with open("com.devework.onnetworkchange.plist", "w", encoding="utf-8") as f:
        f.write(file_content)

    print("[2] Create `com.devework.onnetworkchange.plist` file with success!")


def create_applescript_file(username):
    file_content = (
        f"# get account password from Keychain\n"
        f'set _username to "{username}"\n'
        f'set _password to do shell script "/usr/bin/security find-generic-password -l \'launchd with networkchange\' -a " & _username & " -w || echo denied"\n'
        f"\n"
        f"# failed to get password\n"
        f'if _password is "denied" then\n'
        f'	display dialog "Failed to get the password from Keychain" buttons {"OK"}\n'
        f"	return\n"
        f"end if\n"
        f"\n"
        f'set current_path to (POSIX path of ((path to me as text) & "::"))\n'
        f"\n"
        f"on FileExists(theFile) -- (String) as Boolean\n"
        f'	tell application "System Events"\n'
        f"		if exists file theFile then\n"
        f"			return true\n"
        f"		else\n"
        f"			return false\n"
        f"		end if\n"
        f"	end tell\n"
        f"end FileExists\n"
        f"\n"
        f'if FileExists(current_path & "/dynamic.sh") then\n'
        f'	set file_path to ("\'" & current_path & "/dynamic.sh"\'" & ")\n'
        f"	do shell script file_path user name _username password _password with administrator privileges\n"
        f"else\n"
        f'	set file_path to ("\'" & current_path & "/example.sh"\'" & ")\n'
        f"	do shell script file_path user name _username password _password with administrator privileges\n"
        f"end if\n"
    )

    with open("run.applescript", "w", encoding="utf-8") as f:
        f.write(file_content)

    print("[3] Create `run.applescript` file with success!")


def ln_s_file():
    plist_file_path = f"{dir_path}com.devework.onnetworkchange.plist"
    shell_commend = f"ln -snf {plist_file_path} ~/Library/LaunchAgents/"
    p = subprocess.run(shell_commend, shell=True, stdout=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print("Failed to run `ln -s` script!")
    else:
        print("[4] Run `ln -s` script well.")


def load_plist():
    shell_commend2 = (
        "launchctl load -w ~/Library/LaunchAgents/com.devework.onnetworkchange.plist"
    )
    p = subprocess.run(
        shell_commend2, shell=True, stdout=subprocess.PIPE, text=True, check=True
    )
    print("[5] Launchctl load successfully!")


def unload_plist():
    shell_commend3 = "launchctl unload ~/Library/LaunchAgents/com.devework.onnetworkchange.plist && rm -rf ~/Library/LaunchAgents/com.devework.onnetworkchange.plist"
    p = subprocess.run(
        shell_commend3, shell=True, stdout=subprocess.PIPE, text=True, check=True
    )
    if p.returncode != 0:
        print("Failed to unload plist!")
    else:
        print("Unload launchctl done.")


def main_install():
    script_header()

    user_name = input("Please input your user name: ")
    password = getpass.getpass(f"Please input your password: ")
    script_one = add_to_keychain(user_name, password)
    if not script_one:
        print("Failed to add account to Keychain, please run this script again.")
        delete_from_keychain(user_name)
    else:
        print(
            f"[1] Your user name is {user_name}, Your password will be saved to keychain safely."
        )

    create_plist_file()
    create_applescript_file(user_name)
    ln_s_file()
    load_plist()
    script_footer()

    if len(sys.argv) == 2 and sys.argv[1] == "debug":
        delete_from_keychain(user_name)
        unload_plist()
        print("Debug Mod Done.")


def main_uninstall():
    user_name = input("Please input your user name: ")
    script_two = delete_from_keychain(user_name)
    if not script_two:
        print("Some thing wrong when delete account from keychain.")
    else:
        print("Deleted account from keychain.")
    unload_plist()
    print("All done!")


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] == "debug":
        main_install()
    elif sys.argv[1] == "uninstall":
        main_uninstall()
