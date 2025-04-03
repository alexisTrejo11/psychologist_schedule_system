class HomeDataEntity:
    def __init__(self, patient_count=0, incoming_session_count=0, therapist_name="", profile_picture=None):
        self.patient_count = patient_count
        self.incoming_session_count = incoming_session_count
        self.therapist_name = therapist_name
        self.profile_picture = profile_picture
