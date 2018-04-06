from .generator import CmdLineHandler


def main(args=None):
    """The main routine."""
    try:
        clh = CmdLineHandler()
        clh.cmd_entry_point()
    except KeyboardInterrupt:
        # Don't do anything with keyboard interrupts
        pass


if __name__ == "__main__":
    main()
