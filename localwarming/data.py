import re

class WarmingDataFactory:
    """Provides data to a warming model based on a space-separated file
    provided in the constructor."""
    
    inputFile = None
    
    # Dates and temps are paired lists; should always be same lengths,
    # correspondingly indexed entries align, etc.
    dates = []
    temps = []
    
    def __init__(self, infile):
        self.inputFile = infile
        
        with open(self.inputFile, 'r') as f:
            i = 0
            for line in f:
                match = re.search('\s+(\d{8})\s+(-?\d{1,2}\.\d{1})\s', line)
                if not match:
                    print("Failed to find match for line: {0}".format(line))
                else:
                    self.dates.append(int(match.group(1)))
                    self.temps.append(float(match.group(2)))
                    i = i + 1
    
    def data(self):
        """Get the data contained by the factory for use in other classes."""
        return (self.dates, self.temps)