-- Fictional kit input. These are invented service requests.
CREATE TABLE services (
    service_id INTEGER NOT NULL PRIMARY KEY,
    service_name TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1))
);
CREATE TABLE requests (
    request_id INTEGER NOT NULL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(service_id),
    requested_on TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Draft', 'Submitted', 'Closed')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    closure_reason TEXT
);
