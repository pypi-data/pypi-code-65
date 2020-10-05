class ApiEndpoints:
    def __init__(self):
        self.query_parameters = {}
        self.path_parameters = {}

    def set_requested_fields(self, fields):
        if isinstance(fields, list):
            requested_fields = ",".join(fields) if len(fields) > 0 else "*"
        else:
            requested_fields = fields if fields is not None else None

        if requested_fields is not None:
            self.query_parameters["requestedFields"] = requested_fields

    def set_offset(self, offset):
        if isinstance(offset, int):
            self.query_parameters["offset"] = offset

    def set_limit(self, limit):
        if isinstance(limit, int):
            self.query_parameters["limit"] = limit

    def set_name(self, name):
        if name:
            self.query_parameters["name"] = name

    def set_number(self, number):
        if number:
            self.query_parameters["number"] = number

    def add_query_parameters(self):
        if self.query_parameters:
            _query_params = "&".join(
                [f"{key}={value}" for key, value in self.query_parameters.items()]
            )
            self.query_string = f"{self.query_string}?{_query_params}"


class OrgManagement(ApiEndpoints):
    def __init__(self, session):
        super().__init__(session)


class ProjectManagement(ApiEndpoints):
    def __init__(self, session):
        super().__init__(session)


class Utilities(ApiEndpoints):
    def __init__(self, session):
        super().__init__(session)


class Contacts(OrgManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_contacts = f"{self.base_url}/core/contacts"

    def get_contact(self, contact_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_contacts}/{contact_id}"
        self.add_query_parameters()

        self.path_parameters.update({"contactId": contact_id})

    def get_contact_list(
        self, offset=None, limit=None, name=None, number=None, fields=None
    ):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)
        self.set_name(name)
        self.set_number(number)

        self.query_string = f"{self.base_url_contacts}"
        self.add_query_parameters()

    def create_contact(self):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_contacts}"

    def update_contact(self, contact_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_contacts}/{contact_id}"

        self.path_parameters.update({"contactId": contact_id})


class QueueCalls(OrgManagement):
    def __init__(self, session, queueId):
        super().__init__(session)

        self.add_to_headers("content-type", "application/json")

        self.base_url_queue = f"{self.base_url}/units"
        self.query_string = f"{self.base_url_queue}/{queueId}"

        self.path_parameters.update({"queueId": queueId})


class Documents(OrgManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_docs = f"{self.base_url}/core/documents"

    def add_document_to_project(self, project_id, document_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = (
            f"{self.base_url}/core/projects/{project_id}/documents/{document_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "documentId": document_id}
        )

    def get_document(self, document_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}/{document_id}"

        self.path_parameters.update({"documentId": document_id})

    def get_document_list(self, fields=None, limit=None):

        self.set_requested_fields(fields)
        self.set_limit(limit)

        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}"

    def get_project_document_list(self, project_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url}/core/projects/{project_id}/documents"

        self.path_parameters.update({"projectId": project_id})

    def get_document_download_locator(self, document_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}/{document_id}/locator"

        self.path_parameters.update({"documentId": document_id})

    def create_document_url_for_upload(self):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}"

    def upload_document(self, url):
        self.add_to_headers("content-type", "application/json")

        self.query_string = url

    def add_document_revision(self, document_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}/{document_id}/revisions"

        self.path_parameters.update({"documentId": document_id})

    def update_document_metadata(self, document_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}/{document_id}"

        self.path_parameters.update({"documentId": document_id})

    def delete_document(self, document_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url_docs}/{document_id}"

        self.path_parameters.update({"documentId": document_id})


class ProjectTypes(OrgManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_project_types = f"{self.base_url}/core/projecttypes"

    def get_project_type(self, project_type_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_project_types}/{project_type_id}"
        self.add_query_parameters()

        self.path_parameters.update({"projectTypeId": project_type_id})

    def get_project_type_list(self, offset=None, limit=None, fields=None):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)

        self.query_string = f"{self.base_url_project_types}"
        self.add_query_parameters()

    def get_project_type_section(self, project_type_id, selector, fields=None):

        self.set_requested_fields(fields)

        self.query_string = (
            f"{self.base_url_project_types}/{project_type_id}/sections/{selector}"
        )
        self.add_query_parameters()

        self.path_parameters.update(
            {"projectTypeId": project_type_id, "selector": selector}
        )

    def get_project_type_sections_list(
        self, project_type_id, offset=None, limit=None, fields=None
    ):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)

        self.query_string = f"{self.base_url_project_types}/{project_type_id}/sections"
        self.add_query_parameters()

        self.path_parameters.update({"projectTypeId": project_type_id})

    def get_project_type_phase_list(
        self, project_type_id, offset=None, limit=None, fields=None
    ):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)

        self.query_string = f"{self.base_url_project_types}/{project_type_id}/phases"
        self.add_query_parameters()

        self.path_parameters.update({"projectTypeId": project_type_id})


class Users(OrgManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_users = f"{self.base_url}/core/users"

    def get_user(self, user_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_users}/{user_id}"
        self.add_query_parameters()

        self.path_parameters.update({"userId": user_id})

    def get_current_user(self, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_users}/me"
        self.add_query_parameters()

    def get_user_list(self, offset=None, limit=None, fields=None):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)

        self.query_string = f"{self.base_url_users}"
        self.add_query_parameters()

    def get_users_recent_projects(self, user_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_users}/{user_id}/recentprojects"
        self.add_query_parameters()

        self.path_parameters.update({"userId": user_id})

    def create_user(self):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_users}"

    def remove_user(self, user_id):

        self.query_string = f"{self.base_url_users}/{user_id}"

        self.path_parameters.update({"userId": user_id})


class Projects(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def set_created_since(self, created):
        if created:
            self.query_parameters["createdSince"] = created

    def create_project(self):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}"

    def get_project(self, project_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_project_vitals(self, project_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/vitals"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_project_list(
        self, offset=None, limit=None, name=None, number=None, created=None, fields=None
    ):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)
        self.set_name(name)
        self.set_number(number)
        self.set_created_since(created)

        self.query_string = f"{self.base_url_projects}"
        self.add_query_parameters()

    def update_project(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}"

        self.path_parameters.update({"projectId": project_id})

    def archive_project(self, project_id):

        self.query_string = f"{self.base_url_projects}/{project_id}"

        self.path_parameters.update({"projectId": project_id})

    def toggle_section_visibility(self, project_id):

        self.query_string = f"{self.base_url_projects}/{project_id}/sectionvisibility"

        self.path_parameters.update({"projectId": project_id})


class Notes(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_notes = f"{self.base_url}/core/notes"

    def set_filter_by_type(self, filter_by_type):
        if filter_by_type:
            self.query_parameters["filterByType"] = filter_by_type

    def set_task_filter(self, task_filter):
        if task_filter:
            self.query_parameters["taskFilter"] = task_filter

    def set_created_start(self, created_start):
        if created_start:
            self.query_parameters["createdStart"] = created_start

    def set_created_end(self, created_end):
        if created_end:
            self.query_parameters["createdEnd"] = created_end

    def set_task_target_start(self, task_target_start):
        if task_target_start:
            self.query_parameters["taskTargetStart"] = task_target_start

    def set_task_target_end(self, task_target_end):
        if task_target_end:
            self.query_parameters["taskTargetEnd"] = task_target_end

    def set_hashtags(self, hashtags):
        if hashtags:
            self.query_parameters["hashtags"] = hashtags

    def get_note(self, note_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_notes}/{note_id}"
        self.add_query_parameters()

        self.path_parameters.update({"noteId": note_id})

    def get_note_list(
        self,
        offset=None,
        limit=None,
        filter_by_type=None,
        task_filter=None,
        created_start=None,
        created_end=None,
        task_target_start=None,
        task_target_end=None,
        hashtags=None,
        fields=None,
    ):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_filter_by_type(filter_by_type)
        self.set_task_filter(task_filter)
        self.set_created_start(created_start)
        self.set_created_end(created_end)
        self.set_task_target_start(task_target_start)
        self.set_task_target_end(task_target_end)
        self.set_hashtags(hashtags)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_notes}"
        self.add_query_parameters()

    def get_project_notes_list(
        self,
        project_id,
        offset=None,
        limit=None,
        filter_by_type=None,
        task_filter=None,
        created_start=None,
        created_end=None,
        task_target_start=None,
        task_target_end=None,
        hashtags=None,
        fields=None,
    ):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_filter_by_type(filter_by_type)
        self.set_task_filter(task_filter)
        self.set_created_start(created_start)
        self.set_created_end(created_end)
        self.set_task_target_start(task_target_start)
        self.set_task_target_end(task_target_end)
        self.set_hashtags(hashtags)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url}/core/projects/{project_id}/notes"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def create_note(self):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_notes}"

    def update_note(self, note_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_notes}/{note_id}"

        self.path_parameters.update({"noteId": note_id})


class Tasks(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_tasks = f"{self.base_url}/core/tasks"

    def get_task(self, task_id):

        self.query_string = f"{self.base_url_tasks}/{task_id}"

        self.path_parameters.update({"taskId": task_id})

    def get_task_list(self, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_tasks}"

    def get_project_task_list(self, project_id, offset=None, limit=None, fields=None):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url}/core/projects/{project_id}/tasks"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def create_task(self):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_tasks}"

    def update_tasks(self, tasks):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_tasks}/{tasks}"

        self.path_parameters.update({"tasks": tasks})

    def delete_task(self, task_id):

        self.query_string = f"{self.base_url_tasks}/{task_id}"

        self.path_parameters.update({"taskId": task_id})


class Emails(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def get_project_emails(self, project_id, offset=None, limit=None, fields=None):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/emails"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def add_email_to_project(self, project_id):

        self.query_string = f"{self.base_url_projects}/{project_id}/emails"

        self.path_parameters.update({"projectId": project_id})


class Comments(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_notes = f"{self.base_url}/core/notes"

    def create_comment(self, note_id):

        self.query_string = f"{self.base_url_notes}/{note_id}/comments"

        self.path_parameters.update({"noteId": note_id})

    def get_comment(self, note_id, comment_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_notes}/{note_id}/comments/{comment_id}"
        self.add_query_parameters()

        self.path_parameters.update({"noteId": note_id, "commentId": comment_id})

    def get_comment_list(self, note_id, offset=None, limit=None, fields=None):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_notes}/{note_id}/comments"
        self.add_query_parameters()

        self.path_parameters.update({"noteId": note_id})

    def update_comment(self, note_id, comment_id):

        self.query_string = f"{self.base_url_notes}/{note_id}/comments/{comment_id}"

        self.path_parameters.update({"noteId": note_id, "commentId": comment_id})


class Forms(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def get_forms(self, project_id, section_selector, fields=None):
        self.add_to_headers("Content-Type", "application/json")

        self.set_requested_fields(fields)

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/forms/{section_selector}"
        )
        self.add_query_parameters()

        self.path_parameters.update(
            {"projectId": project_id, "sectionSelector": section_selector}
        )

    def update_form(self, project_id, section_selector):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/forms/{section_selector}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "sectionSelector": section_selector}
        )


class CollectionSections(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def create_collection_item(self, project_id, section_selector):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/collections/{section_selector}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "sectionSelector": section_selector}
        )

    def get_project_collection_item_list(
        self, project_id, section_selector, offset=None, limit=None, fields=None
    ):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_requested_fields(fields)

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/collections/{section_selector}"
        )
        self.add_query_parameters()

        self.path_parameters.update(
            {"projectId": project_id, "sectionSelector": section_selector}
        )

    def get_collection_item(self, project_id, section_selector, unique_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/collections/{section_selector}/{unique_id}"
        self.add_query_parameters()

        self.path_parameters.update(
            {
                "projectId": project_id,
                "sectionSelector": section_selector,
                "uniqueId": unique_id,
            }
        )

    def update_collection_item(self, project_id, section_selector, unique_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/collections/{section_selector}/{unique_id}"

        self.path_parameters.update(
            {
                "projectId": project_id,
                "sectionSelector": section_selector,
                "uniqueId": unique_id,
            }
        )

    def delete_collection_item(self, project_id, section_selector, unique_id):

        self.query_string = f"{self.base_url_projects}/{project_id}/collections/{section_selector}/{unique_id}"

        self.path_parameters.update(
            {
                "projectId": project_id,
                "sectionSelector": section_selector,
                "uniqueId": unique_id,
            }
        )


class Appointments(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def set_from_date_time_utc(self, from_date_time_utc):
        if from_date_time_utc:
            self.query_parameters["fromDateTimeUtc"] = from_date_time_utc

    def set_to_date_time_utc(self, to_date_time_utc):
        if to_date_time_utc:
            self.query_parameters["toDateTimeUtc"] = to_date_time_utc

    def update_appointment(self, project_id, appointment_id):

        self.add_to_headers("Content-Type", "application/json")

        # self.query_string = (
        #     f"{self.base_url_projects}/{project_id}/appointments/{appointment_id}"
        # )
        # self.query_string = f"{self.base_url_projects}/{project_id}/appointments"
        self.query_string = f"{self.base_url}/core/appointments/{appointment_id}"

        # self.path_parameters.update({"projectId": project_id})

    def create_project_appointment(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/appointments"

        self.path_parameters.update({"projectId": project_id})

    def get_project_appointment_list(
        self,
        project_id,
        offset=None,
        limit=None,
        from_date_time_utc=None,
        to_date_time_utc=None,
        fields=None,
    ):

        self.set_requested_fields(fields)
        self.set_offset(offset)
        self.set_limit(limit)
        self.set_from_date_time_utc(from_date_time_utc)
        self.set_to_date_time_utc(to_date_time_utc)

        self.query_string = f"{self.base_url}/core/projects/{project_id}/appointments"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_appointment(self, appointment_id):
        self.add_to_headers("content-type", "application/json")

        self.query_string = f"{self.base_url}/core/appointments/{appointment_id}"

        self.path_parameters.update({"appointmentId": appointment_id})


class Deadlines(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def create_project_deadline(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/deadlines"

        self.path_parameters.update({"projectId": project_id})

    def get_project_deadline_list(
        self, project_id, offset=None, limit=None, fields=None
    ):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/deadlines"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_project_deadline(self, project_id, deadline_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/deadlines/{deadline_id}"
        )
        self.add_query_parameters()

        self.path_parameters.update(
            {"projectId": project_id, "deadlineId": deadline_id}
        )

    def update_project_deadline(self, project_id, deadline_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/deadlines/{deadline_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "deadlineId": deadline_id}
        )

    def delete_project_deadline(self, project_id, deadline_id):

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/deadlines/{deadline_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "deadlineId": deadline_id}
        )


class ProjectContacts(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def set_first_name(self, first_name):
        if first_name:
            self.query_parameters["firstName"] = first_name

    def set_last_name(self, last_name):
        if last_name:
            self.query_parameters["lastName"] = last_name

    def set_full_name(self, full_name):
        if full_name:
            self.query_parameters["fullName"] = full_name

    def set_nick_name(self, nick_name):
        if nick_name:
            self.query_parameters["nickName"] = nick_name

    def set_person_type(self, person_type):
        if person_type:
            self.query_parameters["personType"] = person_type

    def set_phone(self, phone):
        if phone:
            self.query_parameters["phone"] = phone

    def set_email(self, email):
        if email:
            self.query_parameters["email"] = email

    def set_since_last_date_time_utc(self, since_last_date_time_utc):
        if since_last_date_time_utc:
            self.query_parameters["sinceLastDateTimeUtc"] = since_last_date_time_utc

    def get_project_contact_list(
        self,
        project_id,
        offset=None,
        limit=None,
        first_name=None,
        last_name=None,
        full_name=None,
        nick_name=None,
        person_type=None,
        phone=None,
        email=None,
        since_last_date_time_utc=None,
        fields=None,
    ):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_first_name(first_name)
        self.set_last_name(last_name)
        self.set_full_name(full_name)
        self.set_nick_name(nick_name)
        self.set_person_type(person_type)
        self.set_phone(phone)
        self.set_email(email)
        self.set_since_last_date_time_utc(since_last_date_time_utc)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/contacts"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def add_contact_to_project(self, project_id):

        self.query_string = f"{self.base_url_projects}/{project_id}/contacts"

        self.path_parameters.update({"projectId": project_id})

    def update_project_contact(self, project_id, project_contact_id, role):

        self.add_to_headers("role", role)

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/contacts/{project_contact_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "projectContactId": project_contact_id}
        )

    def delete_project_contact(self, project_id, project_contact_id):

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/contacts/{project_contact_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "projectContactId": project_contact_id}
        )


class DeadlineChains(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def create_project_deadline_chain(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/deadlinechains"

        self.path_parameters.update({"projectId": project_id})

    def get_deadline_chain_list(self, project_id, offset=None, limit=None, fields=None):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/deadlinechains"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_deadline_chain(self, project_id, deadline_chain_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/deadlinechains/{deadline_chain_id}"
        )
        self.add_query_parameters()

        self.path_parameters.update(
            {"projectId": project_id, "deadlineChainId": deadline_chain_id}
        )

    def update_deadline_chain(self, project_id, deadline_chain_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = (
            f"{self.base_url_projects}/{project_id}/deadlinechains/{deadline_chain_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "deadlineChainId": deadline_chain_id}
        )

    def delete_deadline_chain(self, project_id, deadline_chain_id):
        self.query_string = (
            f"{self.base_url_projects}/{project_id}/deadlinechains/{deadline_chain_id}"
        )

        self.path_parameters.update(
            {"projectId": project_id, "deadlineChainId": deadline_chain_id}
        )


class Folders(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_folders = f"{self.base_url}/core/folders"

    def set_project_id(self, project_id):
        if project_id:
            self.query_parameters["projectId"] = project_id

    def set_parent_id(self, parent_id):
        if parent_id:
            self.query_parameters["parentId"] = parent_id

    def get_folder(self, folder_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_folders}/{folder_id}"
        self.add_query_parameters()

        self.path_parameters.update({"folderId": folder_id})

    def get_folder_list(
        self, offset=None, limit=None, project_id=None, parent_id=None, fields=None
    ):

        self.set_offset(offset)
        self.set_limit(limit)
        self.set_project_id(project_id)
        self.set_parent_id(parent_id)
        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_folders}"
        self.add_query_parameters()

    def create_folder(self):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_folders}"

    def update_folder(self, folder_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_folders}/{folder_id}"

        self.path_parameters.update({"folderId": folder_id})

    def delete_folder(self, folder_id):
        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_folders}/{folder_id}"

        self.path_parameters.update({"folderId": folder_id})


class ProjectTeam(ProjectManagement):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/projects"

    def get_project_roles(self, project_id, offset=None, limit=None):

        self.set_offset(offset)
        self.set_limit(limit)

        self.query_string = f"{self.base_url_projects}/{project_id}/teamroles"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_project_team(self, project_id, offset=None, limit=None, fields=None):

        self.set_offset(offset)
        self.set_limit(limit)

        self.query_string = f"{self.base_url_projects}/{project_id}/team"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id})

    def get_project_team_member(self, project_id, user_id, fields=None):

        self.set_requested_fields(fields)

        self.query_string = f"{self.base_url_projects}/{project_id}/team/{user_id}"
        self.add_query_parameters()

        self.path_parameters.update({"projectId": project_id, "userId": user_id})

    def create_project_guest_user(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/guestusers"

        self.path_parameters.update({"projectId": project_id})

    def add_project_team_member(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/team"

        self.path_parameters.update({"projectId": project_id})

    def update_project_team_member(self, project_id):

        self.add_to_headers("Content-Type", "application/json")

        self.query_string = f"{self.base_url_projects}/{project_id}/team"

        self.path_parameters.update({"projectId": project_id})

    def remove_project_team_member(self, project_id, user_id):

        self.query_string = f"{self.base_url_projects}/{project_id}/team/{user_id}"

        self.path_parameters.update({"projectId": project_id, "userId": user_id})


class Reports(Utilities):
    def __init__(self, session):
        super().__init__(session)

    def run_saved_report(self):
        pass

    def get_saved_reports_list(self):
        pass


class MassUpdate(Utilities):
    def __init__(self, session):
        super().__init__(session)

        self.base_url_projects = f"{self.base_url}/core/utils/"

    def mass_update_phase(self):
        self.add_to_headers("Content-Type", "application/json")
        self.query_string = f"{self.base_url_projects}/massupdatephase"
        pass

    def mass_update_deadlines(self):
        pass

    def add_hashtag_to_projects(self):
        pass


class Subscriptions(Utilities):
    def __init__(self, session):
        super().__init__(session)

    def get_keys(self):
        pass

    def get_events_list(self):
        self.query_string = f"{self.base_url}/subscriptions/events"

    def create_subscription(self):
        pass

    def get_subscription(self):
        pass

    def get_subscription_list(self):
        self.query_string = f"{self.base_url}/subscriptions"

    def update_subscription(self):
        pass

    def delete_subscription(self):
        pass


class WebhookPayloads(Utilities):
    def __init__(self, session):
        super().__init__(session)


class Traits(Utilities):
    def __init__(self, session):
        super().__init__(session)