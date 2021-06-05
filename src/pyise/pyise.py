import os
import argparse
import sys
from subprocess import Popen, PIPE, DEVNULL
import fnmatch
import shutil
from colorama import init, Fore

synth_template = """
                set PROJECT_NAME @PROJECT_NAME
                set SOURCE_FILES {@SOURCE_FILES}
                if {  [ file exists $PROJECT_NAME.xise ] } {
                        file delete $PROJECT_NAME.xise
                        file delete $PROJECT_NAME.gise
                }

                project new $PROJECT_NAME.xise
                project set family Spartan3E
                project set device xc3s100e
                project set package cp132
                project set speed -4

                 # add all the source HDLs and ucf
                foreach filename $SOURCE_FILES {
                    xfile add $filename
                }
                # get top
                set top @TOP
                # [project get top]
                # do synthesis
                process run "Synthesize - XST"
                """


class PyISE:
    """A Python wrapper for Xilinx ISE.

    This is a Python wrapper for Xilinx ISE with the added functionality
    of batch synthesis and simulation. The console output of batch operations
    are logged.

    Attributes
    ----------
    sourceFiles : list of str
        The Verilog design source files.
    top : str
        Name of the top module.
    simFiles : list of str
        Files used for simulation.
    tbName : str
        Name of the testbench. Does not include file extension. Module name
        must be the same as the file name.
    includeFiles : list of str
        Files that are included in other files.
    xilinx : str
        Path to Xilinx ISE installation
    platform : str
        OS type (lin, lin64, nt, nt64)
    """

    def __init__(self, sourceFiles, top, simFiles, tbName, includeFiles=[],
                 xilinx="/home/bugra/tools/Xilinx/14.7/ISE_DS/ISE",
                 platform="lin64"):
        init(autoreset=True)  # coloroma
        self.includeFiles = includeFiles
        self.sourceFiles = [f for f in includeFiles + sourceFiles
                            if f in sourceFiles and f not in includeFiles]
        self.tbName = tbName
        self.top = top
        self.simFiles = simFiles
        self.xilinx = xilinx
        self.platform = platform
        os.environ['XILINX'] = self.xilinx
        os.environ['PLATFORM'] = self.platform
        os.environ['PATH'] = (os.environ['PATH'] + ':' +
                              os.path.join(self.xilinx, 'bin', self.platform))
        os.environ['LD_LIBRARY_PATH'] = os.path.join(self.xilinx,
                                                     "lib", self.platform)

    def __generateSynthTCL(self, projectName, files):
        """Function for generating synthesis TCL file.

        Generates a TCL file for synthesis which will be interpreted
        by xtclsh to generate an ISE project and synthesize it in
        the current directory.

        Parameters
        ----------
        projectName : str
            Name of the ISE project
        files : list of str
            Files to be added to the project
        """
        text = synth_template
        text = text.replace('@PROJECT_NAME', projectName)
        text = text.replace('@TOP', self.top)
        text = text.replace('@SOURCE_FILES', " ".join(files))
        with open('synth.tcl', 'w') as f:
            f.write(text)

    def __generateSimPRJ(self, files):
        """Function for generating simulation PRJ file.

        Generates a PRJ file for simulation which will be interpreted
        by fuse to generate an ISIM project in the current directory.

        Parameters
        ----------
        files : list of str
            Files to be added to the simulation
        """
        text = ''
        for f in files:
            text += 'verilog work ./' + f + '\n'
        text += "verilog work \"" + self.xilinx + "/verilog/src/glbl.v\""
        with open('sim.prj', 'w') as f:
            f.write(text)

    def __generateSimTCL(self):
        """Function for generating simulation TCL file.

        Generates a simple TCL file with command 'run all' in the current
        directory.
        """
        with open('sim.tcl', 'w') as f:
            f.write('run all')

    def __addWindowsExe(self, str):
        """Function which will add executable file extension if platform is Windows.

        Parameters
        ----------
        str : str
            Executable file name

        Returns
        -------
        str
            Executable name with extension
        """
        if 'nt' in self.platform:
            return str + '.exe'
        return str

    def __printError(self, *str):
        """Prints error text.

        Prints eror text to stdout in red.

        Parameters
        ----------
        *str
            Variable length string list. Will be seperated by space.
        """
        print(Fore.RED + ' '.join(str))

    def __printStatus(self, *str):
        """Prints staus text.

        Prints status text to stdout in green.

        Parameters
        ----------
        *str
            Variable length string list. Will be seperated by space.
        """
        print(Fore.GREEN + ' '.join(str))

    def synthesize(self, folder, file=sys.stdout):
        """Function for synthesizing.

        Does synthesis on the given folder. The folder must contain the source
        and include files. TCL files are generated, they do not need to be in
        the folder.

        Parameters
        ----------
        folder : str
            Path to folder.
        file : file
            Destination to pipe the output to.
        """
        if not os.path.exists(folder):
            self.__printError("Synthesis: Path", folder, "does not exist.")
            return
        self.__printStatus("Synthesis:", folder)
        pwd = os.getcwd()
        os.chdir(folder)
        self.__generateSynthTCL('proj', self.sourceFiles)
        xtclsh = os.path.join(self.xilinx, 'bin', self.platform, 'xtclsh')
        xtclsh = self.__addWindowsExe(xtclsh)
        process = Popen([xtclsh, 'synth.tcl'], stdout=PIPE)
        out, _e = process.communicate()
        out = out.decode('utf-8')
        lines = out.split('\n')
        [print(l, file=file) for l in lines if 'WARNING' in l or 'ERROR' in l]
        os.chdir(pwd)

    def simulate(self, folder, file=sys.stdout):
        """Function for simulation.

        Does simulation on the given folder. The folder must contain the
        source, include and testbench files. PRJ and TCL files are generated,
        they do not need to be in the folder.

        Parameters
        ----------
        folder : str
            Path to folder.
        file : file
            Destination to pipe the output to.
        """
        if not os.path.exists(folder):
            self.__printError("Simulation: Path", folder, "does not exist.")
            return
        self.__printStatus("Simulation:", folder)
        pwd = os.getcwd()
        os.chdir(folder)
        self.__generateSimPRJ(self.simFiles)
        self.__generateSimTCL()
        fuse = os.path.join(self.xilinx, 'bin', self.platform, 'fuse')
        fuse = self.__addWindowsExe(fuse)
        Popen([fuse, '-intstyle', 'ise', '-incremental', '-o', 'sim_exec',
               '-prj', 'sim.prj', 'work.'
               + self.tbName], stdout=DEVNULL).communicate()
        sim_exec = os.path.join(os.getcwd(), 'sim_exec')
        sim_exec = self.__addWindowsExe(sim_exec)
        if self.__addWindowsExe('sim_exec') not in os.listdir():
            self.__printError("Simulation file could not be created")
            os.chdir(pwd)
            return
        process = Popen([sim_exec, '-tclbatch', 'sim.tcl'], stdout=PIPE)
        out, _e = process.communicate()
        out = out.decode('utf-8')
        print(out, file=file)
        os.chdir(pwd)

    def runAll(self, folder, logsFolder, folderPattern="*", gradedFiles=[]):
        """Batch synthesis and simulation function.

        Function for synthesis and simulation of multiple files. It is
        intended to be used in grading. Synhesis and simulation results
        will be logged for each submisson individually. A combined log of
        all submisson logs will also be created.

        Parameters
        ----------
        folder : str
            Root folder containing all the submisson files.
        logsFolder : str
            Folder that will contain all the synthesis and simulation
            logs.
        folderPattern : str
            Regex pattern for finding all the submisson folders.
        gradedFiles : list of str
            Files to be graded. They are expected to be already inside
            the submisson folder.
        """
        folderPattern = folderPattern.rstrip('/')
        patterns = folderPattern.split('/')
        dirs = []
        dirsPrev = os.listdir(folder)
        dirsPrev = [os.path.join(folder, d)
                    for d in dirsPrev if fnmatch.fnmatch(d, patterns[0])]
        for p in patterns[1:]:
            dirs = []
            for d in dirsPrev:
                dirs = os.listdir(d)
                dirs = [os.join(d, f) for f in dirs if fnmatch.fnmatch(f, p)]
            dirsPrev = dirs
        folders = dirsPrev

        if not os.path.exists(logsFolder):
            os.mkdir(logsFolder)
        allFiles = (self.sourceFiles + self.simFiles +
                    self.includeFiles + gradedFiles)
        copyFiles = [i for i in allFiles if i not in gradedFiles and
                     (i in self.sourceFiles or
                      i in self.includeFiles or
                      i in self.simFiles)]
        for f in folders:
            name = ''
            if 'nt' in self.platform:
                name = f.split('\\')[-1] + '.txt'
            else:
                name = f.split('/')[-1] + ".txt"
            for c in copyFiles:
                shutil.copyfile(c, os.path.join(f, c.split('/')[-1]))
            with open(os.path.join(logsFolder, name), 'w') as log:
                log.write('\n\n' + name + '\n')
                log.write("=====SYNTHESIS=====\n")
                self.synthesize(f, file=log)
                log.write("\n=====SIMULATION=====\n")
                self.simulate(f, file=log)

        logs = os.listdir(logsFolder)
        if "combined_log.txt" in logs:
            logs.remove("combined_log.txt")
        with open(os.path.join(logsFolder,
                  "combined_log.txt"), 'w') as combinedLog:
            for l in logs:
                with open(os.path.join(logsFolder, l), 'r') as f:
                    combinedLog.write(f.read())
                    combinedLog.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
             description='Run ISE synthesis and simulation for grading')
    parser.add_argument('--sourceFiles', metavar='-s', type=str, nargs='+',
                        help='Verilog files to be added to the project')
    parser.add_argument('--top', metavar='-t', type=str, nargs='?',
                        help='Name of the top module.')
    parser.add_argument('--simFiles', metavar='-S', type=str, nargs='*',
                        help='Files used for simulation')
    parser.add_argument('--testbench', metavar='-tb', type=str, nargs='?',
                        help='Name of the testbench. \
                        Do not include file extension')
    parser.add_argument('--include', metavar='-i', type=str, nargs='*',
                        help='Files that are included with include macro')
    parser.add_argument('--xilinx', metavar='-x', type=str, nargs='?',
                        help='Path of Xilinx ISE')
    parser.add_argument('--platform', metavar='-p', type=str, nargs='?',
                        help='OS information. (lin, lin64, nt, nt64)')
    parser.add_argument('--folder', metavar='-f', type=str, nargs='?',
                        help='submisson folder')
    parser.add_argument('--logsFolder', metavar='-l', type=str, nargs='?',
                        help='Folder for sim and synth logs')
    parser.add_argument('--folderPattern', metavar='-fp', type=str, nargs='?',
                        help='Regex pattern for submisson folders')
    parser.add_argument('--gradedFiles', metavar='-g', type=str, nargs='+',
                        help='Files names that are going to be graded')
    args = parser.parse_args()
    ise = PyISE(args.sourceFiles, args.top, args.simFiles,
                args.testbench, args.include, args.xilinx,
                args.platform)
    ise.runAll(args.folder, args.logsFolder,
               args.folderPattern, args.gradedFiles)
