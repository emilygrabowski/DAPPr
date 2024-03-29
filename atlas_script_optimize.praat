# Praat script for a Sound and TextGrid sample with two tiers with labelled intervals,
# the first tier labelled by Token, and the second tier labelled by Speaker. Outputs the 
# pitch by 10 millisecond increments within each interval according to Speaker Number, 
# Token number, Token (word), Pitch, and Time.
# author Joy Zhong
#modified by emily grabowski
# Based on a basic script by Daniel Hirst from the website:
# http://uk.groups.yahoo.com/group/praat-users/message/2132
# March 2013

# Tier1 is the Token (word) label and tier2 is the Speaker Number.
tier1= 1 
tier2 = 2  

# Pitch constants
# minf0 = 75
# maxf0 = 500
silence_threshold = 0.03
voicing_threshold = 0.45

# Measure pitch every 10 milliseconds.
timestep = 1/100


form 
sentence Input_audio_file_name
sentence Input_textgrid_file_name
integer Input_min_f0
integer Input_max_f0
sentence outFile 
endform 

#select the sound
sound = Read from file: input_audio_file_name$
selectObject: sound

# load and select textgrid file
textGrid = Read from file: input_textgrid_file_name$
selectObject: textGrid

#sound = selected("Sound")
#textGrid = selected("TextGrid")
#select textGrid

nIntervals1 = Get number of intervals... tier1

# Write to a new file.
deleteFile ("praat.txt")
fileappend praat.txt Token_Number 'tab$' Speaker 'tab$' Token 'tab$' Pitch 'tab$' Time 'newline$'
select sound

# Select the pitch.
To Pitch (ac)... 0.0 input_min_f0 15 no silence_threshold voicing_threshold 0.01 0.35 0.14 input_max_f0
pitch = selected("Pitch")

token = 0     

# Loop through each interval. If that interval has a label, get the tier 1 and tier 2 labels,
# token number, pitch for every 10 ms within that interval, and the corresponding time.
for i to nIntervals1

	select textGrid
	label1$ = Get label of interval... tier1 i  
	#label2$ = Get label of interval... tier2 i 
	
	# Check if interval label is not empty.
	if label1$ != ""
		token += 1

		startTime = Get starting point... tier1 i
		endTime = Get end point... tier1 i
		select pitch

		duration = endTime - startTime
		intervalNumber = duration / timestep
		
		for t from 0 to intervalNumber

			# Increment the time by the timestep.
			time = startTime + t * timestep

			# Get pitch for that time.
			f0 = Get value at time... 'time' Hertz Linear

			# If no pitch is listed for that time, set the pitch to 0.
			#if f0 = undefined
			#	undefined$ = "undefined"
			#	fileappend praat.txt 'token' 'tab$' '1' 'tab$' 'label1$' 'tab$' 'undefined$' 'tab$' 'time:2''newline$'

			#If we want to use 0's instead of "undefined" in the case that the pitch isn't listed:
			if f0 = undefined
					f0 = 0
					fileappend praat.txt 'token' 'tab$' '1' 'tab$' 'label1$' 'tab$' 'f0' 'tab$' 'time:2''newline$'


			# Append results to the file previously created. 
			else
				fileappend praat.txt 'token' 'tab$' '1' 'tab$' 'label1$' 'tab$' 'f0:2' 'tab$' 'time:2' 'newline$'
			
			endif

		endfor

	endif

endfor

select pitch
Remove
select textGrid
Remove
select sound
Remove
