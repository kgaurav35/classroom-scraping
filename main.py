import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload


# Define the scopes required for accessing Google Classroom API
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.rosters.readonly',
          'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
          'https://www.googleapis.com/auth/classroom.coursework.students.readonly']

# Define the directory to save the downloaded files
SAVE_DIRECTORY = r'C:\Users\vyaan\Downloads\Google Classroom Files'


def authenticate():
    """Authenticates and returns a Google Classroom service object."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # Build and return the Classroom service object
    service = build('classroom', 'v1', credentials=creds)
    return service


def download_files(service, course_id):
    """Downloads all files from the specified course."""
    course_work = service.courses().courseWork().list(
        courseId=course_id).execute()
    course_work = course_work.get('courseWork', [])

    for work in course_work:
        if work['workType'] == 'ASSIGNMENT':
            attachments = work['assignment']['materials']
            for attachment in attachments:
                if attachment['driveFile']:
                    file_id = attachment['driveFile']['driveFile']['id']
                    file_name = attachment['driveFile']['driveFile']['title']
                    file_path = os.path.join(SAVE_DIRECTORY, file_name)

                    request = service.drive().files().get_media(fileId=file_id)
                    fh = open(file_path, 'wb')
                    downloader = MediaIoBaseDownload(fh, request)

                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()


def main():
    # Authenticate the user and create a Google Classroom service object
    service = authenticate()

    # Get a list of all courses
    courses = service.courses().list().execute()
    courses = courses.get('courses', [])

    # Iterate over each course and download files
    for course in courses:
        course_id = course['id']
        download_files(service, course_id)


if __name__ == '__main__':
    main()
