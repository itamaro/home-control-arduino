# Tick length (in microseconds) as set in IRremote lib
g_TickMicroSec = 50.0

class AcSample(object):
    def __init__(self, pwr, mode, fan, temp, decoded_value=None, raws=None):
        self.pwr = pwr
        self.mode = mode
        self.fan = fan
        self.temp = temp
        self.decoded_value = decoded_value
        self.signals = list() 
        if raws:
            self.add_raw_signals(raws)
        self.av_signal = None

    def str(self):
        return '%s %s %s %d' % (self.pwr, self.mode, self.fan, self.temp)
    
    def add_raw_signals(self, raws):
        # The raw data for received IR measures the duration of successive
        # spaces and marks in 50us ticks.
        # The first measurement is the gap,
        # the space before the transmission starts.
        # The last measurement is the final mark.
        # Gaps are listed as negative numbers,
        # while marks as positive numbers.
        raws_list = raws
        if type(raws) == str:
            raws_list = [raws]
        self.signals.extend([map(int, rs.split()[3:]) for rs in raws_list])
        # (leaving out the prefix "Raw (XX):", and the initial gap)
    
    def calc_average_signal(self):
        if 1 < len(set([len(sig) for sig in self.signals])):
            raise RuntimeError('Raw signals are not of the same size')
        self.av_signal = list(self.signals[0])
        for sig in self.signals[1:]:
            for i, t in enumerate(sig):
                self.av_signal[i] += t
        for i in xrange(len(self.av_signal)):
            self.av_signal[i] /= len(self.signals)

    def normalize(self):
        # Calculate average signal over all raw signals
        self.calc_average_signal()
        # Check that every raw signal is "similar enough" to the average one
        for n, sig in enumerate(self.signals):
            for i, t in enumerate(sig):
                diff = abs(t - self.av_signal[i])
                if diff > int(2 * g_TickMicroSec):
                    print 'Signal %s #%d differs by %d in position %d' %   \
                          (self.str(), n+1, diff, i)
                    return False
        return True

    def arr_name(self):
        return 'uSendBuff_%s_%s_%s_%d' % (
                self.pwr, self.mode, self.fan, self.temp)

    def to_arduino_array(cmd):
        return 'PROGMEM prog_uint16_t %s[] = {%d, %s};' % (cmd.arr_name(),
                len(cmd.av_signal),
                ', '.join(str(int(g_TickMicroSec *
                                  round(abs(t / g_TickMicroSec))))
                          for t in cmd.av_signal))
    
def to_time_sig(sig):
    values = [1]
    for tl in sig:
        val = 0.9 if tl > 0 else 0.1
        for t in range(int(abs(tl) / g_TickMicroSec)):
            values.append(val)
    return values

def graph_av_signals(commands):
    import matplotlib.pyplot as plt
    base = len(commands) * 100 + 11
    plt.figure(1)
    for idx, cmd in enumerate(commands):
        plt.subplot(base + idx)
        plt.title('A/C-Remote, %s' % (cmd.str()))
        time_sig = to_time_sig(cmd.av_signal)
        plt.plot([t * 0.05 for t in xrange(len(time_sig))],
                  time_sig, lw=0.7)
        plt.ylim([0.0,1.0])
        plt.ylabel('IR Mark / Space')
    plt.xlabel('time [msec]')
    plt.show()

def generate_arduino_code(commands):
    for cmd in commands:
        print cmd.to_arduino_array()
    print ''
    # Assume other Arduino code created a state using the following variables:
    #   pwr  - enum { Toggle, Leave }
    #   mode - enum { Cool, Heat, Fan, Dry }
    #   fan  - enum { Auto, Low, Medium, High }
    #   temp - int
    print 'prog_uint16_t * getAcSendBuff() {'
    for cmd in commands:
        print '\tif ( (%s == pwr) && (%s == mode) &&(%s == fan) && '   \
              '(%s == temp) ) { return %s; }' % (cmd.pwr, cmd.mode, cmd.fan,
                                                 cmd.temp, cmd.arr_name())
    print '\treturn 0;\n}'

def load_from_raw(data_dir):
    # Go over files in the data dir, and parse as an AC command sample file
    # Each file should be named according to the command state, in the form:
    # `pwr-mode-fan-temp`
    # and contain in plain text the output of the Arduino IRACReceiver
    # program, possibly multiple results per file (to improve accuracy)
    import os
    commands = list()
    for root, _, files in os.walk(data_dir):
        for raw_file in files:
            # Initialize an AcSample object from raw file name
            pwr, mode, fan, temp = raw_file.split('-')
            sample = AcSample(pwr, mode, fan, int(temp))
            value = None
            with open(os.path.join(root, raw_file), 'r') as f:
                for line in f:
                    line = line.strip()
                    if 0 == line.find('0x'):
                        # it's a decoded-value line
                        newval = int(line[:line.find(' ')], 16)
                        if not sample.decoded_value:
                            sample.decoded_value = newval
                        elif sample.decoded_value != newval:
                            print 'There are inconsistencies in file "%s"' % \
                                  (raw_file)
                    elif 0 == line.find('Raw'):
                        # it's a raw-list line
                        sample.add_raw_signals(line)
            if sample.normalize():
                commands.append(sample)
            else:
                print 'Skipping sample for command', sample.str()
    return commands

if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description='IR Analysis Tool.')
    parser.add_argument('-d', '--dumps-dir', default='test-data/IRdumps',
                        help='Path to a directory containing IR dump files')
    subparsers = parser.add_subparsers()
    # Add IR signals graphing subcommand
    parser_graph = subparsers.add_parser('graph', help='Graph the IR signals')
    parser_graph.set_defaults(func=graph_av_signals)
    # Add Arduino code generation subcommand
    parser_code = subparsers.add_parser('code', help='Generate Arduino code')
    parser_code.set_defaults(func=generate_arduino_code)
    
    args = parser.parse_args()
    args.func(load_from_raw(args.dumps_dir))
