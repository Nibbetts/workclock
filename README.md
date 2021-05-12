# workclock
A punch-in / punch-out terminal work clock system, for easy time recording, suited for separating time on different personal projects.

    NOTE: These commands assume your alias for 'workclock.py' is 'clock'; if this is not
    the case, alter each command accordingly.

    NOTE: Project names are not case sensitive.

## Terminal Commands

`workclock.py alias [alias_name] [bashrc_file]`

  A way of installing the program so that you have a convenient
  alias for 'workclock.py'.

    alias_name
        May be used to specify something other than 'clock' as the
        time clock punching command that runs this file as a script.

    bashrc_file
        Unless you know what you're doing,
        do not use this option; it is the path to the particular
        terminal settings file on which to append the alias command.

`clock`

  Print a status update, indicating the current/last project, whether
  or not you are clocked in and when, current time, total project
  hours including current punch, and current punch duration.

`clock in [project_name] [hour_of_in:minute_of_in]`

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

`clock out [hour_of_out:mintue_of_out]`

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

`clock change project_name`

  If clocked in, clocks out of the current project, and into
  project_name. If not clocked in, simply changes the current/last
  project to project_name. Both situations give a report; the former is
  a conglomeration of clock-in / clock-out reports, the latter is more
  like the report given by the status update, or simple 'clock' command.
    
    project_name
        The project to switch to.
        
`clock project [project_name]`

  Gives a full report of the given or current project, including project
  name, whether current, whether clocked in, total project hours, number
  of clock-ins, and details about all past punches.

    project_name
        Project to report on. Optional; if not used, will use current.

`clock list`

  Gives a report listing all projects and their total times. If clocked
  in, the total for the current project will be shown as without the
  current punch, but with that off to the side. Also reports what the
  the last/current project is, and whether or not you are currently
  clocked in.
