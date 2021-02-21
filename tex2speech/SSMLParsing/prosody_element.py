from SSMLParsing.ssml_element_node import SSMLElementNode
import xml.etree.ElementTree as ET

# Prosody for Volume attribute
class ProsodyElement(SSMLElementNode):
    def __init__(self, volume = None, rate = None, pitch = None, duration = None):
        super().__init__()
        
        if volume is not None:
            self.volume = self._assignVolume(volume)
        
        if rate is not None:
            self.rate = self._assignRate(rate);

        if pitch is not None:
            self.pitch = self._assignPitch(pitch);

        if duration is not None:
            self.duration = self._assignDuration(duration);

    # Assigns volume depending on dB or actual words (e.g., x-soft, soft)
    def _assignVolume(self, value):
        temp = ""
        if value[1].isnumeric():
            tempVal = value[:-2]
            temp= int(tempVal)
        else:
            if value == 'x-soft':
                temp = -6
            elif value == 'soft':
                temp= -3
            elif value == 'medium':
                temp = 0
            elif value == 'loud':
                temp= 3
            elif value == 'x-loud':
                temp = 6
            else:
                temp = 0

        return temp

    # Assigns rate depending on percentage between 20% and 200% or through
    # words (e.g., x-slow, slow, etc)
    def _assignRate(self, rate):
        temp = ""
        if rate[0].isnumeric():
            tempVal = int(rate[:-1])

            # Rate is between 20% and 200%
            if tempVal > 200:
                temp = 200;
            elif tempVal < 20:
                temp = 20;
            else:
                temp= int(tempVal)
        else:
            if rate == 'x-slow':
                temp = 60
            elif rate == 'slow':
                temp = 80
            elif rate == 'medium':
                temp = 100
            elif rate == 'fast':
                temp = 120
            elif rate == 'x-fast':
                temp = 140
            else:
                temp = 100

        return temp

    # Assigns pitch depending on -20dB or +20dB or words (e.g., x-low, low etc)
    def _assignPitch(self, pitch):
        temp = ""
        if pitch[1].isnumeric():
            tempVal = pitch[:-1]
            temp= int(tempVal)
        else:
            if pitch == 'x-low':
                temp = -20
            elif pitch == 'low':
                temp = -10
            elif pitch == 'medium':
                temp = 0
            elif pitch == 'high':
                temp = 10
            elif pitch == 'x-high':
                temp = 20
            else:
                temp = 0;

        return temp

    # Assigns duration in respect to using ms (converts s to ms)
    def _assignDuration(self, duration):
        temp = ""

        if len(duration) - 3 >= 0:
            if duration[len(duration) - 2].isnumeric():
                temp = int(duration[:-1]) * 1000
            else:
                temp = duration[:-2]
        else:
            temp = duration[:-1] * 1000

        return temp

    # Gets medium volume of nested and self element
    def _mediumVolume(self, nestedVolume):
        mid = (self.volume + self._assignVolume(nestedVolume))/2

        if str(mid[0]) == '-':
            return mid + "dB"
        else:
            return "+" + mid + "dB"

    # Gets medium rate of nested and self element
    def _mediumRate(self, nestedRate):
        mid = (self.rate + self._assignRate(nestedRate))/2;
        return str(mid) + "%"

    # Gets medium pitch of nested and self element
    def _mediumPitch(self, nestedPitch):
        mid = (self.pitch + self._assignRate(nestedPitch))/2;

        if mid[0] == '-':
            return str(mid) + "%"
        else:
            return "+" + str(mid) + "%"

    # Gets medium duration depending on nested and self element
    def _mediumDuration(self, nestedDuration):
        mid = (self.duration + self._assignRate(nestedDuration))/2;
        return str(mid) + "ms"

    # Grabs self volume (+/- n dB)
    def getVolume(self):
        if str(self.volume)[0] == '-': 
            return str(self.volume) + "dB"
        else:
            return "+" + str(self.volume) + "dB"

    # Grabs self rate (n%)
    def getRate(self):
        return str(self.rate) + "%"

    # Grabs self pitch (+/- n%)
    def getPitch(self):
        if str(self.pitch)[0] == '-':
            return str(self.pitch) + "%"
        else:
            return "+" + str(self.pitch) + "%"

    # Grabs self duration (n ms)
    def getDuration(self):
        return str(self.duration) + "ms"

    def _update(self):
        pass

    def _getXMLElement(self):
        pass

    def __str__(self):
        a = "ProsodyElement"
        if self.getHeadText() != "":
            a = '"' + self.getHeadText() + '"' + " " + a
        if self.getTailText() != "":
            a += " " + '"' + self.getTailText() + '"'
        return a

    __repr__ = __str__
