# Discord Scraper

Release Date: October 3, 2017 @ 10:13 UTC-0

# Discord App Tutorial

Step 1:
Open your Discord app and enter the app settings.
![vwJ4kp5.png](https://i.imgur.com/vwJ4kp5.png "Step 1")

Step 2:
Traverse to Appearance and enable Developer Mode if it is disabled.
![35zu4Wt.png](https://i.imgur.com/35zu4Wt.png "Step 2a")
![YEad6fw.png](https://i.imgur.com/YEad6fw.png "Step 2b")

Step 3:
Close the app settings and press CTRL + SHIFT + I to open the Developer panel.

Step 4:
Expand the Local Storage area on the left-side of the Developer panel.
Copy the value of "token" into the config.json file.
![Z7SHpYs.png](https://i.imgur.com/Z7SHpYs.png "Step 4a")
![5tekl6c.png](https://i.imgur.com/5tekl6c.png "Step 4b")

Step 5:
Close the Developer panel and right-click on the server icon and copy ID.
Paste the server ID into the config.json file.
![32VP97z.png](https://i.imgur.com/32VP97z.png "Step 5a")
![NXQM9zx.png](https://i.imgur.com/NXQM9zx.png "Step 5b")

Step 6:
Right-click on the channel name and copy ID.
Paste the channel ID into the config.json file.
![okhdZtQ.png](https://i.imgur.com/okhdZtQ.png "Step 6a")
![vTD8zL4.png](https://i.imgur.com/vTD8zL4.png "Step 6b")

Step 7:
Run the script to start the downloading process.

# Discord Website Tutorial

Step 1:
Login to your Discord account.
![Gr1b8NZ.png](https://i.imgur.com/Gr1b8NZ.png "Step 1")

Step 2:
Press CTRL + SHIFT + I to open the Developer Tools panel.

Step 3:
Expand the Local Storage area on the left-side of the Developer Tools panel.
Copy the value of "token" into the config.json file.
![Z7SHpYs.png](https://i.imgur.com/Z7SHpYs.png "Step 3a")
![5tekl6c.png](https://i.imgur.com/5tekl6c.png "Step 3b")

Step 4:
Close the Developer Tools panel and right-click on the server icon and copy ID.
Paste the server ID into the config.json file.
![qGB3IXJ.png](https://i.imgur.com/qGB3IXJ.png "Step 4a")
![NXQM9zx.png](https://i.imgur.com/NXQM9zx.png "Step 4b")

Step 5:
Right-click on the channel name and copy ID.
Paste the channel ID into the config.json file.
![6gO2LPF.png](https://i.imgur.com/6gO2LPF.png "Step 5a")
![vTD8zL4.png](https://i.imgur.com/vTD8zL4.png "Step 5b")

Step 6:
Run the script to start the downloading process.

# Note
**You can copy in multiple channels on multiple servers if you want to.**

# Changelog (DD-MM-YYYY)

13-11-2018 - Released:
* Implemented a new concept from the experimental branch.
* Updated the experimental branch to match the master branch.
* I will find a method of alleviating the duplicate images/videos issue.
* I will fix up the commenting and make the code easier on the eyes.

28-08-2018 - Added Experimental Branch:
* Python 3 version of script now uses a separate config.
* MFA token now goes in the separate config to help avoid accidental leakage of one's MFA token.
* Multiple channel and server support added.
* Replaced the requests module with http.client module which is built-in to Python 3.7.

07-04-2018 - Beta Fix #3:
* Fixed threading issue (too many concurrent threads)
* Fixed filename issues when grabbing files with similar filenames (still a potential issue with large amounts of files but significantly less issues)

07-04-2018 - Beta Fix #2:
* Fixed problems when downloading from channels with less than 25 images/videos as the older scripts assumed more than 25 images/videos in the channel.
* I will incorporate a better method of grabbing images where there's less corruptions and less missing photos.

21-02-2018 - Beta Update #1:
* Updated this readme to include warning information
* Created a version for those running Python 3
* Updated the Python 2 version to match the Python 3 version with threading support

03-10-2017 - Beta Fix #1:
* Fixed issue with URL appending offset query information ad infinitum.
* Fixed issue with uninitialized opener data when grabbing multiple pages of JSON data.
* Added new function to allow for the resetting of opener data when grabbing JSON data.

03-10-2017 - Beta Release:
* The first release of the script.
* Not meant for production use.
* Still has bugs to fix and features to implement.