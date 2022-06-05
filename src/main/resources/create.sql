CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
)

CREATE TABLE Appointment (
    Appt_ID INT,
    Patient varchar(255) REFERENCES Patients(Username),
    Time date,
    Caregiver varchar(255) REFERENCES Caregivers(Username),
    Vaccine varchar(255) REFERENCES Vaccines(Name),
    PRIMARY KEY (Appt_ID, Patient, Time, Caregiver, Vaccine)
)