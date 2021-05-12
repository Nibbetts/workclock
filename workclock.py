"""
Work Time Clock

By: Nathan Tibbetts
11 May 2021

DESCRIPTION:
    For easy clock-in clock-out like time recording behavior, suited for
    separating time on different projects.

USAGE:
    These assume your alias for 'workclock.py' is 'clock'; if this is not
    the case, alter each command accordingly.

    NOTE: Project names are not case sensitive.

    workclock.py alias [alias_name] [bashrc_file]
        A way of installing the program so that you have a convenient
        alias for 'workclock.py'.
        
        alias_name
            May be used to specify something other than 'clock' as the
            time clock punching command that runs this file as a script.

        bashrc_file
            Unless you know what you're doing,
            do not use this option; it is the path to the particular
            terminal settings file on which to append the alias command.

    clock
        Print a status update, indicating the current/last project, whether
        or not you are clocked in and when, current time, total project
        hours including current punch, and current punch duration.

    clock in [project_name] [hour_of_in:minute_of_in]
        Clock in. If project name is not present, the last active project
        will be used. Reports on the current project, time, and total
        project hours.
        
        hour_of_in:minute_of_in
            This is only used to put this
            clock-in back in time, as a way to correct a missed clock-in.
            These should be integers. This is the time of day, not the
            duration of the punch, and must be measured in 24-hour time.
            To go further back than the current day you must edit the
            punches.txt file yourself.

        Example: 'clock in DatabaseProj 13:05' for retroactively clocking
        in at 1:05 PM on the project named 'DatabaseProj'.
    
    clock out [hour_of_out:mintue_of_out]
        Clock out of the current project. Reports on the current project,
        time in, time out, total project hours, and punch duration.
        
        hour_of_out:minute_of_out
            This is only used to put this clock-out back in time, as a way
            to correct a missed clock-out. These should be integers. This is
            the time of day, not the duration of the punch, and must be
            measured in 24-hour time. To go further back than the current
            day you must edit the punches.txt file yourself.

        Example: 'clock out 13:05' for retroactively clocking out of the
        current project at 1:05 PM.

    clock change project_name
        If clocked in, clocks out of the current project, and into
        project_name. If not clocked in, simply changes the current/last
        project to project_name. Both situations give a report; the former is
        a conglomeration of clock-in / clock-out reports, the latter is more
        like the report given by the status update, or simple 'clock' command.
        
        project_name
            The project to switch to.

    clock project [project_name]
        Gives a full report of the given or current project, including project
        name, whether current, whether clocked in, total project hours, number
        of clock-ins, and details about all past punches.

        project_name
            Project to report on. Optional; if not used, will use current.

    clock list
        Gives a report listing all projects and their total times. If clocked
        in, the total for the current project will be shown as without the
        current punch, but with that off to the side. Also reports what the
        the last/current project is, and whether or not you are currently
        clocked in.
"""

from datetime import datetime
from time import strftime
from pathlib import Path
from os.path import join
from sys import argv



IN_OUT_SEP   = " -> "
PUNCH_SEP    = " | "
HEADER0      = "WORK CLOCK PUNCHES, STARTED "
HEADER1      = "Last Project: "
HEADER2      = "Clocked In: "
HEADER3      = "Project" + PUNCH_SEP + "Total" + PUNCH_SEP + "Punches"
HEADER_L     = 4
TIMEF        = "%c"
SEC_PER_HOUR = 3600
YES          = 'YES'
NO           = 'NO'
PUNCHES_FILE = "punches.txt"
PATH         = Path(__file__).parent.absolute()
SCRIPT_PATH  = Path(__file__).absolute()
PUNCHES_PATH = join(PATH, PUNCHES_FILE)
BASHRC_PATH  = "~/.bashrc"


def parse_file(project=None):
    # Read the lines from the file
    with open(PUNCHES_PATH, 'r+') as f:
        lines = f.read().splitlines()
        # Format if new file
        if len(lines) < HEADER_L:
            lines = [
                HEADER0 + strftime(TIMEF),
                HEADER1,
                HEADER2 + NO,
                HEADER3,
            ]

    # Find the correct project name
    finished = lines[2][len(HEADER2):] == YES
    last_proj = lines[1][len(HEADER1):]
    if project is None:
        if not len(last_proj):
            raise ValueError("Must specify project if no history")
        project = last_proj
    else:
        project = project.lower()

    return lines, finished, project


def parse_line(lines, project, finished):
    """ Finds and parses the line for the project."""
    # Find the corresponding line index
    # project should already be lower case
    length = len(project)
    for i, l in enumerate(lines[HEADER_L:]):
        if l[:length] == project:
            new = False
            i += HEADER_L
            break
    else:
        i += HEADER_L + 1
        new = True
    
    # Process the line
    line = project + PUNCH_SEP + "0" + PUNCH_SEP if new else lines[i].split(PUNCH_SEP)
    last = None if finished else datetime.strptime(line[-1], TIMEF)
    times = []
    for punch in (line[2:] if finished else (line[2:-1])):
        time_in, time_out = punch.split(IN_OUT_SEP)
        time_in  = datetime.strptime(time_in,  TIMEF)
        time_out = datetime.strptime(time_out, TIMEF)
        times.append(time_out - time_in)

    return line, i, last, new, times


def clock_in(project=None, previous_time=None):
    # Get the data
    lines, finished, project   = parse_file(project=project)
    line, index, _, new, times = parse_line(lines, project, finished)
    if not finished:
        raise RuntimeError('Correct missed clock-out first by clocking out with added argument for (24-hr formatted) time of day, "hour:minute"')
    if previous_time:
        h, m = previous_time.split(':')
        in_time = datetime(previous_time.year, previous_time.month, previous_time.day, int(h), int(m))
    else:
        in_time = datetime.now()

    # Format the data
    total = sum(times).total_seconds() / SEC_PER_HOUR
    in_time = in_time.strftime(TIMEF)

    # Modifying the lines for the file
    lines[2] = HEADER2 + YES
    lines[1] = HEADER1 + project
    line.append(in_time)
    line = PUNCH_SEP.join(line)
    if new:
        lines.append(line)
    else:
        lines[index] = line

    # Write to file
    with open(PUNCHES_PATH, 'w') as f:
        f.write('\n'.join(lines))

    # Report
    print(f"CLOCK IN, Project: '{project}'")
    print(f"IN: {in_time}")
    print(f"'{project}' Total Hrs: {total:.2f}")


def clock_out(previous_time=None):
    # Get the data
    lines, finished, project    = parse_file(project=None)
    line, index, last, _, times = parse_line(lines, project, finished)
    if finished:
        raise RuntimeError('Correct missed clock-in first by clocking in with added argument for (24-hr formatted) time of day, "hour:minute"')
    if previous_time:
        h, m = previous_time.split(':')
        out = datetime(previous_time.year, previous_time.month, previous_time.day, int(h), int(m))
        if out <= last:
            raise ValueError("Invalid time, less than clock-in time. If clock out was after midnight, correct by punching out at midnight, then making an extra punch in before punching out.")
    else:
        out = datetime.now()

    # Calculations and format conversions
    punch = out - last
    total = sum(times) + punch
    punch = punch.total_seconds() / SEC_PER_HOUR
    total = total.total_seconds() / SEC_PER_HOUR
    out = out.strftime(TIMEF)

    # Modifying the lines for the file
    lines[2] = HEADER2 + NO
    line[-1] += IN_OUT_SEP + out
    line[1] = f"{total:.2f}"
    line = PUNCH_SEP.join(line)
    lines[index] = line

    # Write to file
    with open(PUNCHES_PATH, 'w') as f:
        f.write('\n'.join(lines))

    # Report
    print(f"CLOCK OUT, Project: '{project}'")
    print(f"IN: {last.strftime(TIMEF)}, OUT: {out}")
    print(f"'{project}' Total Hrs: {total:.2f}, Current Punch: {punch:.2f}")


def change_project(project):
    """ Changes current project, punching in and out if necessary."""
    # Get the data
    project = project.lower()
    lines, finished, last_project = parse_file(project=None)
    line1, i1, last1, _, times1   = parse_line(lines, last_project, finished)
    line2, i2, _,  new2, times2   = parse_line(lines, project,      finished)
    now = datetime.now()

    # Format the data
    total1 = sum(times1)
    if not finished:
        punch1 = now - last1
        total1 += punch1
        punch1 =  punch1.total_seconds() / SEC_PER_HOUR
    total1 =      total1.total_seconds() / SEC_PER_HOUR
    total2 = sum(times2).total_seconds() / SEC_PER_HOUR
    now = now.strftime(TIMEF)

    # Modifying the lines for the file
    lines[1] = HEADER1 + project
    if not finished:

        # Clock-Out
        line1[-1] += IN_OUT_SEP + now
        line1[1] = f"{total1:.2f}"
        line1 = PUNCH_SEP.join(line1)
        lines[i1] = line1

        # Clock-In
        line2.append(now)
    line2 = PUNCH_SEP.join(line2)
    if new2:
        lines.append(line2)
    else:
        lines[i2] = line2

    # Write to file
    with open(PUNCHES_PATH, 'w') as f:
        f.write('\n'.join(lines))

    # Report
    if finished:
        print(f"CURRENTLY CLOCKED OUT, Project Switched From: '{last_project}', To: '{project}'")
        print(f"NOW: {now}")
        print(f"'{last_project}' Total Hrs: {total1:.2f}")
        print(f"'{project}' Total Hrs: {total2:.2f}")
    else:
        print(f"CLOCK OUT, Project: '{last_project}'")
        print(f"CLOCK IN,  Project: '{project}'")
        print(f"'{last_project}' IN: {last1.strftime(TIMEF)}, NOW: {now}")
        print(f"'{last_project}' Total Hrs: {total1:.2f}, Current Punch: {punch1:.2f}")
        print(f"'{project}' Total Hrs: {total2:.2f}")


def check_time():
    # Get the data
    lines, finished, project = parse_file(project=None)
    _, _, last, _, times     = parse_line(lines, project, finished)
    now = datetime.now()

    # Calculations and format conversions
    total = sum(times)
    if not finished:
        delta = now - last
        total += delta
        delta = delta.total_seconds() / SEC_PER_HOUR
    total     = total.total_seconds() / SEC_PER_HOUR
    now = now.strftime(TIMEF)

    # Report
    if finished:
        print(f"CURRENTLY CLOCKED OUT, Last Project: '{project}'")
        print(f"NOW: {now}")
        print(f"'{project}' Total Hrs: {total:.2f}")
    else:
        print(f"CURRENTLY CLOCKED IN, Project: '{project}'")
        print(f"IN: {last.strftime(TIMEF)}, NOW: {now}")
        print(f"'{project}' Total Hrs: {total:.2f}, Current Punch: {delta:.2f}")


def report_project(project=None):
    # Get the data
    lines, finished, current_project = parse_file(project=None)
    if project is None: project = current_project
    else: project = project.lower()
    line, _, last, _, times = parse_line(lines, project, finished)
    now = datetime.now()

    # Calculations and format conversions
    total = sum(times)
    if not finished:
        delta = now - last
        total += delta
        delta = delta.total_seconds() / SEC_PER_HOUR
    total     = total.total_seconds() / SEC_PER_HOUR
    now = now.strftime(TIMEF)

    # Report
    addon = "" if finished else f", Current Punch: {delta:.2f}"
    current = project == current_project
    print(f"PROJECT REPORT FOR: '{project}'")
    print(f"Is Current: {YES if current else NO}, Clocked In: {(NO if finished else YES) if current else 'NOT CURRENT'}")
    print(f"Total Hrs: {total:.2f}" + addon)
    print(f"Number of Clock-Ins: {len(times) + (not finished)}")
    print("PUNCHES:\n\t" + line.join('\n\t'))


def list_projects():
    # Get the data
    lines, finished, project = parse_file(project=None)
    _, _, last, _, _         = parse_line(lines, project, finished)
    now = datetime.now()

    # Calculations and format conversions
    if finished:
        addon = ""
    else:
        delta = now - last
        delta = delta.total_seconds() / SEC_PER_HOUR
        addon = f" +{delta:.2f}"

    # Report
    print("WORK CLOCK PROJECTS")
    print(f"{'Last' if finished else 'Current'} Project: '{project}'")
    print(f"Clocked In: {NO if finished else YES}")
    print(f"PROJECT \tTOTAL +current")
    for l in lines:
        proj  = l[0]
        hours = l[1] + (addon if proj == project else "")
        print(f"{proj:15s} {hours}")


def alias(name='clock', install_path=BASHRC_PATH):
    with open(BASHRC_PATH, 'a') as f:
        f.write(f'\nalias {name}="{SCRIPT_PATH}"')
    print("Alias '{name}' added to {BASHRC_PATH}")
    if install_path == BASHRC_PATH:
        print("All new terminals opened will reflect this change.")

    
if __name__ == "__main__":
    # A terminal command to clock in on a new or different-than-last
    #   project might look like: 'clock in DatabaseProj'

    try:
        # Prep the first additional argument
        if len(argv) > 1:
            arg1 = argv[1].lower()

            # Command to set up the 'clock' or other aliases;
            #   this would have to look like 'python3 workclock.py alias'.
            #   This must be done after you've got this script where it will reside.
            if arg1 == "alias":
                alias(*argv[2:])

            # Command to change projects, whether clocked in or out
            elif arg1 == "change":
                change_project(argv[2])
                
            # Command to list all projects and their total hours
            elif arg1 == "list":
                list_projects()

            # Command to list all information on a project
            elif arg1 == "project":
                report_project(*argv[2:])

            # Command to clock in to the last worked-on project, or for a given project
            elif arg1 == "in":
                assert len(argv) <= 4, "No arguments allowed after previous_time"
                if ':' in argv[2]:
                    clock_in(None, argv[2])
                else:
                    clock_in(*argv[2:])

            # Command to clock out of the current project
            elif arg1 == "out":
                assert len(argv) <= 3, "Only previous_time argument allowed for clock-out"
                assert ':' in argv[2]
                clock_out(*argv[2:])

            # Command to print documentation
            elif arg1 == "help":
                print(__doc__)
        
        # No additional argument means it's just a status check
        else:
            check_time()

    # Some error arose, so let's print a usage statement and the documentation
    except:
        print("Incorrect usage. Here's the documentation:")
        print(__doc__)