import math
import decimal
import bisect

class SP_Path:

    def __init__(self, chart):
        self.chart = chart
        self.sp_activations = []
        self.sp_note_pos = []

        self.sp_bar = 0
        self.sp_bar_length = self.chart.resolution * 64

        self.add_sp_notes()
        self.set_basic_sp_path()

    def add_sp_notes(self):
        s = 0
        sp_phrases = self.chart.sp_phrases
    
        while s < len(sp_phrases):
            self.sp_note_pos.append(self.chart.notes[bisect.bisect_right(
            [note["position"] for note in self.chart.notes], 
            sp_phrases[s]["position"] + sp_phrases[s]["length"] - 1)]["position"])  

            s += 1

            if s == len(sp_phrases):
                break     
            
        print(str(self.sp_note_pos))

    def can_activate_sp(self):
        return self.sp_bar >= self.sp_bar_length / 2

    def add_sp_activation(self, sp_activation):
        self.sp_activations.append(sp_activation)

    def set_basic_sp_path(self):
        pos = 0
        song_length = self.chart.notes[len(self.chart.notes) - 1]["position"] \
            + self.chart.notes[len(self.chart.notes) - 1]["length"]

        while pos < song_length:
            
            if pos >= self.sp_note_pos[0]:
                self.sp_bar += self.chart.resolution * 16
                self.sp_note_pos.remove(self.sp_note_pos[0])
                if not self.sp_note_pos:
                    break

            if self.can_activate_sp():
                sp_activation = {
                    "position": pos,
                    "length": self.sp_bar
                }
                self.sp_bar = 0
                self.add_sp_activation(sp_activation)

            pos += self.chart.resolution

        print(str([sp_activation["position"] for sp_activation in self.sp_activations]))


class Chart:
    NOTE_SCORE = 50
    MY_HEART_SCORE = 78762
    BROKED_SCORE = 55850
    KILLING_SCORE = 393643
    MEUERRO_SCORE = 159402
    BATCOUNTRY_SCORE_NO_SOLO = 363378
    BATCOUNTRY_SCORE = 390278
    SOULLESS4_SCORE = 2079014
    BROKED_AVGMULT = 3.777

    def __init__(self, difficulty, resolution):
        self.difficulty = difficulty
        self.resolution = resolution
        self.sections = []
        self.notes = []  
        self.solo_sections = []
        self.sp_phrases = []

        self.sp = 0
        self.sl = 0
        self.sa = 0

    def add_sp_path(self):
        self.sp_path = SP_Path(self) 

    def pos_in_phrase(self, position):
        while self.sp < len(self.sp_phrases):
            if self.sp_phrases[self.sp]["position"] + self.sp_phrases[self.sp]["length"] - 1 < position:  
                self.sp += 1
            else:
                return self.sp_phrases[self.sp]["position"] <= position
            
        return False   

    def pos_in_solo(self, position):
        while self.sl < len(self.solo_sections):
            if self.solo_sections[self.sl]["position"] + self.solo_sections[self.sl]["length"] < position:  
                self.sl += 1
            else:
                return self.solo_sections[self.sl]["position"] <= position
            
        return False   

    def pos_in_path(self, position):
        while self.sa < len(self.sp_path.sp_activations):
            if self.sp_path.sp_activations[self.sa]["position"] + self.sp_path.sp_activations[self.sa]["length"] < position:  
                self.sa += 1
            else:
                return self.sp_path.sp_activations[self.sa]["position"] <= position
            
        return False   

    def add_note(self, note):
        self.notes.append(note)

    def add_solo_section(self, solo_section):
        self.solo_sections.append(solo_section)

    def add_sp_phrase(self, sp_phrase):
        self.sp_phrases.append(sp_phrase)

    def total_unique_notes(self):
        notes_count = 0

        for i in range(len(self.notes)):
            if i == 0:
                notes_count += 1
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                notes_count += 1

        return notes_count

    def calc_unote_index(self, note):
        note_index = self.notes.index(note)
        unique_note_index = 0

        for i in range(note_index + 1):
            if i == 0:
                unique_note_index += 1
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                unique_note_index += 1

        return unique_note_index

    def calc_note_multiplier(self, unote_index):
        if unote_index > 30:
            return 4
        else:
            return math.floor(unote_index / 10) + 1

    def is_unique_note(self, note):
        note_index = self.notes.index(note)

        if note_index == 0:
            return True
        elif self.notes[note_index]["position"] > self.notes[note_index - 1]["position"]:
            return True
        
        return False

    def calculate_score(self, start, end, time_signatures, include_note_lengths):
        score = 0
        multiplier = 1
        unique_note_index = 0

        for i in range(start, end):

            unique_note = self.is_unique_note(self.notes[i])

            if unique_note:
                if multiplier < 4:
                    unique_note_index += 1
                    if unique_note_index > 30:
                        multiplier = 4
                    else:
                        multiplier = math.floor(unique_note_index / 10) + 1

            score += self.NOTE_SCORE * multiplier

            if self.pos_in_solo(self.notes[i]["position"]):
                score += self.NOTE_SCORE * 2

            if include_note_lengths and self.notes[i]["length"] > 0 and unique_note:
                score += self.NOTE_SCORE / 2 * multiplier * self.notes[i]["length"] / self.resolution
                #score = int(round(score))
                score = int(math.ceil(score))
               # score = score.quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP)
            """
            if i == 0:
                print(str(unique_note_index) + " - " + str(score))
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                print(str(unique_note_index) + " - " + str(score))  
            """             

        return score

    """
        Since the song"s length is based on the song file, the average multiplier is calculated using 
        the chart"s length, not the song.
    """
    def avg_multiplier(self):

        multiplier = 1

        song_length = self.notes[len(self.notes) - 1]["position"] \
            + self.notes[len(self.notes) - 1]["length"]

        if song_length == 0:
            return multiplier

        sum_multiplier = 0       
        unique_note_index = 0

        # multinc_pos = []

        for i in range(len(self.notes)):
            if self.is_unique_note(self.notes[i]):
                if multiplier < 4:
                    unique_note_index += 1
                    if unique_note_index == 30:
                        multiplier = 4
                        # multinc_pos.append(self.notes[i]["position"])
                        # break
                    else:
                        multiplier = math.floor(unique_note_index / 10) + 1
                        '''
                        next_multiplier = math.floor(unique_note_index / 10) + 1
                        if next_multiplier > multiplier:
                            multiplier = next_multiplier
                            multinc_pos.append(self.notes[i]["position"])
                        '''

                sum_multiplier += multiplier

        '''
        multiplier = 1

        for position in range(0, song_length):
            if multinc_pos:
                if position >= multinc_pos[0]:
                    multiplier += 1
                    multinc_pos.remove(multinc_pos[0])

            sum_multiplier += multiplier

        return sum_multiplier / song_length
        '''
        return sum_multiplier / self.total_unique_notes()

class Song:

    DIFFICULTIES = {
        "ExpertSingle": "Expert Guitar", 
        "HardSingle": "Hard Guitar", 
        "MediumSingle": "Medium Guitar", 
        "EasySingle": "Easy Guitar",
        "ExpertDoubleBass": "Expert Bass",
        "HardDoubleBass": "Hard Bass", 
        "MediumDoubleBass": "Medium Bass", 
        "EasyDoubleBass": "Easy Bass",
        "ExpertDoubleRhythm": "Expert Rhythm",
        "HardDoubleRhythm": "Hard Rhythm", 
        "MediumDoubleRhythm": "Medium Rhythm", 
        "EasyDoubleRhythm": "Easy Rhythm",
        "ExpertKeyboard": "Expert Keys", 
        "HardKeyboard": "Hard Keys", 
        "MediumKeyboard": "Medium Keys", 
        "EasyKeyboard": "Easy Keys",
        "ExpertDrums": "Exper tDrums",
        "HardDrums": "Hard Drums", 
        "MediumDrums": "Medium Drums", 
        "EasyDrums": "Easy Drums"
    }

    def __init__(self, name, charter, resolution=192):
        self.name = name if name else "Unknown"
        self.charter = charter if charter else "Unknown"
        self.resolution = resolution 
        self.bpms = []
        self.time_signatures = []
        self.sections = []
        self.charts = []


    def add_section(self, section):
        self.sections.append(section)

    def add_bpm(self, bpm):
        self.bpms.append(bpm)

    def add_time_signature(self, time_signature):
        self.time_signatures.append(time_signature)

    def add_chart(self, chart):
        self.charts.append(chart)