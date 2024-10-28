export interface CreateContactSchema {
    email: string
}

export interface GetContactSchema {
    id: string // uuid
    first_name: string;
    last_name: string;
}

export interface GetContactsSchema {
    contacts: GetContactSchema[];
}

export type ContactsState = {
    contactList: GetContactSchema[]
    currentContactId: string | null
}
