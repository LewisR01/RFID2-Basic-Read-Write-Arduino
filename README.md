# RFID2-Basic-Read-Write-Arduino
A basic sketch written for an Arduino nano to write and read values to an NTAG213 using a M5Stack RFID2 (W1850S) module. 

This sketch and python script allow the writing and reading of data using an M5Stack RFID2 device and NTAG213s controlled by an Arduino Nano over a COM port. I personally had trouble getting it to work as it doesn't seem to be quite the same as the standard MFRC522 devices. The python script is a simple GUI with a connection button and status indicator. It has a text box for entering your value to be sent to the tag, and a button to write, zeroise, and read the data on the tag.

I am not a tech wizard or software in any sense whatsoever and relied on help from the notorious ChatGPT for this. It took a very very long time to get it to help me narrow down the faults I was having. I am only sharing this as the information on the internet currently is limited for this particular device. This should be a simple 'plug and play' solution for most people. 

One of the main issues I have is that the NTAG213s I am using seem to have the 5th, 6th, and 7th values locked off. Probably an "of course" moment for anyone reading but it was news to me. The GUI still shows these values (may edit to not have them print at a later date) and will also require you to enter the full 7 two digit values when writing (another for the future.) However when reading you will see that they remain unchanged (I assume.) I tried only addressing the first 4 values in my arduino code but it just fired back a could not write error everytime so I've left it for now.

I am new to this whole idea of arduino and makering and especially posting a repository so apologies in advance if I have made a mistake.


