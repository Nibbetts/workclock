"""
 Work Time Clock
 
 By: Nathan Tibbetts
 11 May 2021
 
 DESCRIPTION:
     For easy clock-in clock-out like time recording behavior, suited for
     separating time spent on different projects.
 
     NOTE: Does not run in the background between clocking in and out.

 USAGE:
     NOTE: Creates a 'punches.txt' file to store timecard information in in
     the same directory as the script; this file must not move, or it will be
     recreated from scratch.
 
     NOTE: These assume your alias for 'workclock.py' is 'clock'; if this is not
     the case, alter each command accordingly.
 
     NOTE: Project names are not case sensitive.
 
     NOTE: No method is provided for deleting old projects, or for other
     more complex edits, but it is fairly easy to edit the punches.txt file
     itself.
 
     workclock.py alias [alias_name] [bashrc_file]
         A way of installing the program so that you have a convenient
         alias for 'workclock.py'. This should not be done until this script
         is where you want it to reside. NOTE that this does not remove
         previous installations, so if you need to remove it or reinstall it,
         you'll have to edit the bashrc_file used yourself.
         
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
 
     clock help
         Print this documentation.
 
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
 
     clock switch project_name
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

from datetime import datetime, timedelta
from time import strftime
from pathlib import Path
from os.path import join, expanduser, exists
from sys import argv, exc_info
from traceback import format_exception



IN_OUT_SEP   = " -> "
PUNCH_SEP    = " | "
HEADER0      = "WORK CLOCK PUNCHES, STARTED: "
HEADER1      = "Last Project: "
HEADER2      = "Clocked In: "
HEADER3      = "Project" + PUNCH_SEP + "Total" + PUNCH_SEP + "Punches"
HEADER_L     = 4
TIMEF        = "%c"
SEC_PER_HOUR = 3600
SEC_PER_MIN  = 60
YES          = 'YES'
NO           = 'NO'
PUNCHES_FILE = "punches.txt"
PATH         = Path(__file__).parent.absolute()
SCRIPT_PATH  = Path(__file__).absolute()
PUNCHES_PATH = join(PATH, PUNCHES_FILE)
BASHRC_PATH  = join(expanduser('~'), ".bashrc")


def parse_file(project=None):
    # Read the lines from the file
    if exists(PUNCHES_PATH):
        with open(PUNCHES_PATH, 'r') as f:
            lines = f.read().splitlines()
    # Format if new file
    else:
        lines = [
            HEADER0 + strftime(TIMEF),
            HEADER1,
            HEADER2 + NO,
            HEADER3,
        ]

    # Find the correct project name
    finished = lines[2][len(HEADER2):] == NO
    last_proj = lines[1][len(HEADER1):]
    if project is None:
        if not len(last_proj):
            raise ValueError("Must specify project if no history")
        project = last_proj
    else:
        project = project.lower()

    return lines, finished, project


def parse_line(lines, project, project_in):
    """ Finds and parses the line for the project."""
    # NOTE: project_in, here, is whether or not the given project is currently
    #   clocked in, rather than whether any is, like 'finished' in other functions.
    # Find the corresponding line index
    # project should already be lower case
    length = len(project)
    i = 0
    for i, l in enumerate(lines[HEADER_L:]):
        if l[:length] == project:
            new = False
            i += HEADER_L
            break
    else:
        i += HEADER_L + 1
        new = True
    
    # Process the line
    line = [project, "0"] if new else lines[i].split(PUNCH_SEP)
    last = None if project_in else datetime.strptime(line[-1], TIMEF)
    times = []
    for punch in (line[2:] if project_in else (line[2:-1])):
        time_in, time_out = punch.split(IN_OUT_SEP)
        time_in  = datetime.strptime(time_in,  TIMEF)
        time_out = datetime.strptime(time_out, TIMEF)
        times.append(time_out - time_in)

    return line, i, last, new, times


def clock_in(project=None, previous_time=None):
    # Get the data
    lines, finished, project = parse_file(project=project)
    if not finished:
        print('ALREADY CLOCKED IN; Correct missed clock-out first by clocking out with added argument for (24-hr formatted) time of day, "hour:minute"')
        return
    line, index, _, new, times = parse_line(lines, project, finished)
    in_time = datetime.now()
    if previous_time:
        h, m = previous_time.split(':')
        in_time = datetime(in_time.year, in_time.month, in_time.day, int(h), int(m))

    # Format the data
    total = sum(t.total_seconds() for t in times)
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
    with open(PUNCHES_PATH, 'w+') as f:
        f.write('\n'.join(lines))

    # Report
    if new:
        print(f"Created Project: '{project}'")
    print(f"CLOCK IN, Project: '{project}'")
    print(f"IN: {in_time}")
    print(f"'{project}' Total Hrs: {fnum(total)}")


def clock_out(previous_time=None):
    # Get the data
    lines, finished, project = parse_file(project=None)
    if finished:
        print('ALREAD CLOCKED OUT; Correct missed clock-in first by clocking in with added argument for (24-hr formatted) time of day, "hour:minute"')
        return
    line, index, last, _, times = parse_line(lines, project, finished)
    if previous_time:
        h, m = previous_time.split(':')
        out = datetime(previous_time.year, previous_time.month, previous_time.day, int(h), int(m))
        if out <= last:
            print("Invalid time, less than clock-in time. If clock out was after midnight, correct by punching out at midnight, then making an extra punch in before punching out.")
            return
    else:
        out = datetime.now()

    # Calculations and format conversions
    punch = out - last
    times.append(punch)
    total = sum(t.total_seconds() for t in times)
    punch = punch.total_seconds()
    out = out.strftime(TIMEF)

    # Modifying the lines for the file
    lines[2] = HEADER2 + NO
    line[-1] += IN_OUT_SEP + out
    line[1] = fnum(total)
    line = PUNCH_SEP.join(line)
    lines[index] = line

    # Write to file
    with open(PUNCHES_PATH, 'w+') as f:
        f.write('\n'.join(lines))

    # Report
    print(f"CLOCK OUT, Project: '{project}'")
    print(f"IN: {last.strftime(TIMEF)}, OUT: {out}")
    print(f"'{project}' Total Hrs: {fnum(total)}, Current Punch: {fnum(punch)}")


def switch_project(project):
    """ Changes current project, punching in and out if necessary."""
    # Get the data
    project = project.lower()
    lines, finished, last_project = parse_file(project=None)
    line1, i1, last1, _, times1   = parse_line(lines, last_project, finished)
    line2, i2, _,  new2, times2   = parse_line(lines, project,      True)
    now = datetime.now()

    # Format the data
    if not finished:
        punch1 = now - last1
        times1.append(punch1)
        punch1 = punch1.total_seconds()
    total1 = sum(t.total_seconds() for t in times1)
    total2 = sum(t.total_seconds() for t in times2)
    now = now.strftime(TIMEF)

    # Modifying the lines for the file
    lines[1] = HEADER1 + project
    if not finished:

        # Clock-Out
        line1[-1] += IN_OUT_SEP + now
        line1[1] = fnum(total1)
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
    with open(PUNCHES_PATH, 'w+') as f:
        f.write('\n'.join(lines))

    # Report
    if new2:
        print(f"Created Project: '{project}'")
    if finished:
        print(f"CURRENTLY CLOCKED OUT, Project Switched From: '{last_project}', To: '{project}'")
        print(f"NOW: {now}")
        print(f"'{last_project}' Total Hrs: {fnum(total1)}")
        print(f"'{project}' Total Hrs: {fnum(total2)}")
    else:
        print(f"CLOCK OUT, Project: '{last_project}'")
        print(f"CLOCK IN,  Project: '{project}'")
        print(f"'{last_project}' IN: {last1.strftime(TIMEF)}, NOW: {now}")
        print(f"'{last_project}' Total Hrs: {fnum(total1)}, Current Punch: {fnum(punch1)}")
        print(f"'{project}' Total Hrs: {fnum(total2)}")


def check_time():
    # Get the data
    lines, finished, project = parse_file(project=None)
    _, _, last, _, times     = parse_line(lines, project, finished)
    now = datetime.now()

    # Calculations and format conversions
    if not finished:
        delta = now - last
        times.append(delta)
        delta = delta.total_seconds()
    total = sum(t.total_seconds() for t in times)
    now = now.strftime(TIMEF)

    # Report
    if finished:
        print(f"CURRENTLY CLOCKED OUT, Last Project: '{project}'")
        print(f"NOW: {now}")
        print(f"'{project}' Total Hrs: {fnum(total)}")
    else:
        print(f"CURRENTLY CLOCKED IN, Project: '{project}'")
        print(f"IN: {last.strftime(TIMEF)}, NOW: {now}")
        print(f"'{project}' Total Hrs: {fnum(total)}, Current Punch: {fnum(delta)}")


def report_project(project=None):
    # Get the data
    lines, finished, current_project = parse_file(project=None)
    if project is None: project = current_project
    else: project = project.lower()
    current = project == current_project
    line_finished = finished if current else True
    line, _, last, new, times = parse_line(lines, project, line_finished)
    now = datetime.now()

    # Calculations and format conversions
    if not line_finished:
        delta = now - last
        times.append(delta)
        delta = delta.total_seconds()
    total = sum(t.total_seconds() for t in times)
    now = now.strftime(TIMEF)

    # Report
    if new:
        print(f"Created Project: '{project}'")
    addon = "" if line_finished else f", Current Punch: {fnum(delta)}"
    print(f"PROJECT REPORT FOR: '{project}'")
    print(f"""Is Current: {YES if current else NO}, Clocked In: {YES if not line_finished else NO if finished else "'" + current_project + "'"}""")
    print(f"Total Hrs: {fnum(total)}" + addon)
    print(f"Number of Clock-Ins: {len(times)}") # Includes current now
    print("PUNCHES:\n\t" + '\n\t'.join(line[2:]))


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
        delta = delta.total_seconds()
        addon = f" +{fnum(delta)}"

    # Report
    print("WORK CLOCK PROJECTS")
    print(f"{'Last' if finished else 'Current'} Project: '{project}'")
    print(f"Clocked In: {NO if finished else YES}")
    print(f"PROJECT \tTOTAL +current")
    for l in lines[HEADER_L:]:
        line = l.split(PUNCH_SEP)
        proj  = line[0]
        hours = line[1] + (addon if proj == project else "")
        print(f"{proj:15s} {hours}")


def alias(name='clock', install_path=BASHRC_PATH):
    with open(BASHRC_PATH, 'a') as f:
        f.write(f'\nalias {name}="python3 {SCRIPT_PATH}"')
    print(f"Alias '{name}' added to {BASHRC_PATH}")
    if install_path == BASHRC_PATH:
        print("All new terminals opened will reflect this change.")

    
def fnum(sec):
    """ Format seconds to hours:minutes:seconds"""
    hrs = int(sec // SEC_PER_HOUR)
    r = sec % SEC_PER_HOUR
    mins = int(r // SEC_PER_MIN)
    sec = int(r % SEC_PER_MIN)
    return f"{hrs}:{mins}:{sec}"


if __name__ == "__main__":
    # A terminal command to clock in on a new or different-than-last
    #   project might look like: 'clock in DatabaseProj'
    new = not exists(PUNCHES_PATH)

    try:
        # Prep the first additional argument
        if len(argv) > 1:
            arg1 = argv[1].lower()

            # If no punches.txt file yet, deny certain commands that need
            #   a previously defined project to exist. You can still get an error
            #   if you create a file yourself that is in the wrong format though,
            #   or is missing a last/current project.
            if new and arg1 in ["change", "list", "project", "out"]:
                print(f"Cannot execute '{arg1}'; no punches yet.")

            # Command to set up the 'clock' or other aliases;
            #   this would have to look like 'python3 workclock.py alias'.
            #   This must be done after you've got this script where it will reside.
            elif arg1 == "alias":
                alias(*argv[2:])

            # Command to switch projects, whether clocked in or out
            elif arg1 == "switch":
                switch_project(argv[2])
                
            # Command to list all projects and their total hours
            elif arg1 == "list":
                list_projects()

            # Command to list all information on a project
            elif arg1 == "project":
                report_project(*argv[2:])

            # Command to clock in to the last worked-on project, or for a given project
            elif arg1 == "in":
                assert len(argv) <= 4, "No arguments allowed after previous_time"
                if len(argv) >= 3 and ':' in argv[2]:
                    clock_in(None, argv[2])
                else:
                    clock_in(*argv[2:])

            # Command to clock out of the current project
            elif arg1 == "out":
                assert len(argv) <= 3, "Only previous_time argument allowed for clock-out"
                if len(argv) == 3:
                    assert ':' in argv[2]
                clock_out(*argv[2:])

            # Command to print documentation
            elif arg1 == "help":
                print(__doc__)

            else:
                print(f'Unknown clock command "{arg1}". Valid commands are:')
                print('["", "help", "alias", "in", "out", "switch", "list", "project"]')
        
        # No additional argument means it's just a status check
        elif new:
            print("No punches yet, no status to check.")
        else:
            check_time()

    # Some error arose, so let's print a usage statement and the documentation
    except:
        print("".join(format_exception(*exc_info())))
        print("Incorrect usage. Use the argument `help` to print documentation.")