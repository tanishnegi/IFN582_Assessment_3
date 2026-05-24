DROP DATABASE IF EXISTS sharespace;

CREATE DATABASE sharespace;

USE sharespace;


CREATE TABLE users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    firstname VARCHAR(100) NOT NULL,

    lastname VARCHAR(100) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    phone VARCHAR(20) NOT NULL,

    role ENUM('admin', 'seller', 'buyer') NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE properties (

    id INT AUTO_INCREMENT PRIMARY KEY,

    seller_id INT NOT NULL,

    title VARCHAR(255) NOT NULL,

    property_type VARCHAR(50) NOT NULL,

    price DECIMAL(10,2) NOT NULL,

    suburb VARCHAR(100) NOT NULL,

    city VARCHAR(100) NOT NULL,

    postcode VARCHAR(10) NOT NULL,

    bedrooms INT NOT NULL,

    bathrooms INT NOT NULL,

    occupants INT NOT NULL,

    compatibility_score DECIMAL(3,1) DEFAULT 0,

    image VARCHAR(255),

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (seller_id)
        REFERENCES users(id)
        ON DELETE CASCADE

);


CREATE TABLE preferences (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL UNIQUE

);


CREATE TABLE property_preferences (

    property_id INT NOT NULL,

    preference_id INT NOT NULL,

    PRIMARY KEY (property_id, preference_id),

    FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE CASCADE,

    FOREIGN KEY (preference_id)
        REFERENCES preferences(id)
        ON DELETE CASCADE

);


CREATE TABLE user_preferences (

    user_id INT NOT NULL,

    preference_id INT NOT NULL,

    PRIMARY KEY (user_id, preference_id),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (preference_id)
        REFERENCES preferences(id)
        ON DELETE CASCADE

);


CREATE TABLE enquiries (

    enquiry_id INT AUTO_INCREMENT PRIMARY KEY,

    buyer_id INT NOT NULL,

    property_id INT NOT NULL,

    subject VARCHAR(255) NOT NULL,

    message TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (buyer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE CASCADE

);


CREATE TABLE offers (

    id INT AUTO_INCREMENT PRIMARY KEY,

    buyer_id INT NOT NULL,

    property_id INT NOT NULL,

    offered_price DECIMAL(10,2) NOT NULL,

    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (buyer_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE CASCADE

);



INSERT INTO users
(firstname, lastname, email, password, phone, role)

VALUES

('Admin', 'One', 'admin1@sharespace.com', '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e', '0400000001', 'admin'),

('Admin', 'Two', 'admin2@sharespace.com', '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e', '0400000002', 'admin'),

('Sarah', 'Mitchell', 'sarah@sharespace.com', '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e', '0400000003', 'seller'),

('Daniel', 'Roberts', 'daniel@sharespace.com', '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e', '0400000004', 'seller'),

('Rahul', 'Harlapur', 'rahul@sharespace.com', '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e', '0400000005', 'buyer'),

('Emily', 'Chen', 'emily@sharespace.com', '8776f108e247ab1e2b323042c049c266407c81fbad41bde1e8dfc1bb66fd267e', '0400000006', 'buyer');



INSERT INTO preferences (name)

VALUES

('Clean'),

('Pet Friendly'),

('Non-Smoker'),

('Student'),

('Quiet'),

('Social'),

('Early Riser'),

('Night Owl');



INSERT INTO properties
(
    seller_id,
    title,
    property_type,
    price,
    suburb,
    city,
    postcode,
    bedrooms,
    bathrooms,
    occupants,
    compatibility_score,
    image,
    description
)

VALUES

(
    3,
    'Modern Shared Apartment Near CBD',
    'Shared Apartment',
    220,
    'Brisbane CBD',
    'Brisbane',
    '4000',
    2,
    1,
    2,
    4.5,
    'img/pexels-artbovich-7019026.jpg',
    'Modern shared apartment located close to public transport and universities.'
),

(
    3,
    'Bright Shared Apartment',
    'Shared Apartment',
    240,
    'South Brisbane',
    'Brisbane',
    '4101',
    2,
    2,
    2,
    4.7,
    'img/pexels-pixabay-271618.jpg',
    'Spacious apartment with natural lighting and furnished shared spaces.'
),

(
    3,
    'Luxury Entire Apartment',
    'Entire Apartment',
    450,
    'New Farm',
    'Brisbane',
    '4005',
    2,
    2,
    2,
    4.9,
    'img/pexels-fotoaibe-1571453.jpg',
    'Premium entire apartment overlooking the Brisbane River.'
),

(
    4,
    'Quiet Shared House',
    'Shared House',
    210,
    'Toowong',
    'Brisbane',
    '4066',
    4,
    2,
    4,
    4.6,
    'img/pexels-john-tekeridis-21837-1428348.jpg',
    'Peaceful shared home suitable for students and professionals.'
),

(
    4,
    'Affordable Private Room',
    'Private Room',
    180,
    'Woolloongabba',
    'Brisbane',
    '4102',
    1,
    1,
    1,
    4.2,
    'img/pexels-andrew-3201763.jpg',
    'Affordable furnished private room near public transport.'
),

(
    4,
    'Clean Shared Apartment',
    'Shared Apartment',
    230,
    'West End',
    'Brisbane',
    '4101',
    2,
    1,
    2,
    4.8,
    'img/pexels-artbovich-7195864.jpg',
    'Well-maintained apartment with peaceful shared living spaces.'
),

(
    3,
    'Student Shared Apartment',
    'Shared Apartment',
    260,
    'St Lucia',
    'Brisbane',
    '4067',
    3,
    2,
    3,
    4.6,
    'img/pexels-pixabay-271618.jpg',
    'Shared apartment located close to UQ campus.'
),

(
    3,
    'Spacious Shared House',
    'Shared House',
    240,
    'Indooroopilly',
    'Brisbane',
    '4068',
    4,
    2,
    4,
    4.4,
    'img/pexels-artbovich-7019026.jpg',
    'Large shared house with backyard and study area.'
),

(
    3,
    'Modern Studio Apartment',
    'Studio',
    320,
    'South Bank',
    'Brisbane',
    '4101',
    1,
    1,
    1,
    4.8,
    'img/pexels-pixabay-271618.jpg',
    'Modern studio apartment with gym and pool access.'
),

(
    4,
    'Budget Private Room',
    'Private Room',
    170,
    'Annerley',
    'Brisbane',
    '4103',
    1,
    1,
    1,
    4.1,
    'img/pexels-fotoaibe-1571453.jpg',
    'Budget-friendly private room in quiet neighbourhood.'
),

(
    4,
    'Social Shared Apartment',
    'Shared Apartment',
    270,
    'Kelvin Grove',
    'Brisbane',
    '4059',
    3,
    2,
    3,
    4.7,
    'img/pexels-pixabay-271618.jpg',
    'Perfect shared apartment for social student living.'
),

(
    4,
    'Private Room Near City',
    'Private Room',
    240,
    'Highgate Hill',
    'Brisbane',
    '4101',
    1,
    1,
    1,
    4.3,
    'img/pexels-fotoaibe-1571453.jpg',
    'Fully furnished private room close to Brisbane CBD.'
),

(
    3,
    'Luxury Studio Apartment',
    'Studio',
    380,
    'Fortitude Valley',
    'Brisbane',
    '4006',
    1,
    1,
    1,
    4.9,
    'img/pexels-pixabay-271618.jpg',
    'Luxury studio apartment with premium amenities.'
),

(
    4,
    'Family Friendly Shared House',
    'Shared House',
    250,
    'Chermside',
    'Brisbane',
    '4032',
    4,
    2,
    4,
    4.5,
    'img/pexels-fotoaibe-1571453.jpg',
    'Large shared house with parking and outdoor area.'
),

(
    3,
    'Nightlife Shared Apartment',
    'Shared Apartment',
    230,
    'Fortitude Valley',
    'Brisbane',
    '4006',
    2,
    1,
    2,
    4.2,
    'img/pexels-andrew-3201763.jpg',
    'Shared apartment located near restaurants and nightlife.'
);

INSERT INTO property_preferences
(property_id, preference_id)

VALUES

(1,2),
(1,4),
(1,5),

(2,1),
(2,3),

(3,4),

(4,1),
(4,5),

(5,4),

(6,1),
(6,3),

(7,4),
(7,5),

(8,1),
(8,5),

(9,1),
(9,3),

(10,4),

(11,6),
(11,4),

(12,3),
(12,5),

(13,1),
(13,7),

(14,2),
(14,6),

(15,8),
(15,6);



INSERT INTO user_preferences
(user_id, preference_id)

VALUES

(5,1),
(5,3),
(5,5),

(6,2),
(6,6),
(6,8);


INSERT INTO offers
(buyer_id, property_id, offered_price, status)

VALUES

(5, 3, 270, 'accepted'),

(6, 9, 330, 'rejected'),

(5, 11, 250, 'pending');


CREATE TABLE property_images (

    id INT AUTO_INCREMENT PRIMARY KEY,

    property_id INT NOT NULL,

    image VARCHAR(255) NOT NULL,

    display_order INT NOT NULL,

    FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE CASCADE

);


INSERT INTO property_images
(property_id, image, display_order)
VALUES
(1, 'img/pexels-artbovich-7019026.jpg', 1),
(1, 'img/pexels-cottonbro-4781415.jpg', 2),
(1, 'img/pexels-cottonbro-5158945.jpg', 3),

(2, 'img/pexels-pixabay-271618.jpg', 1),
(2, 'img/pexels-pavel-danilyuk-7776179.jpg', 2),

(3, 'img/pexels-fotoaibe-1571453.jpg', 1),
(3, 'img/pexels-artbovich-7195864.jpg', 2),

(4, 'img/pexels-john-tekeridis-21837-1428348.jpg', 1),
(4, 'img/pexels-curtis-adams-1694007-7028071.jpg', 2),

(5, 'img/pexels-andrew-3201763.jpg', 1),
(5, 'img/pexels-thomas-plets-1139798-5403840.jpg', 2),

(6, 'img/pexels-artbovich-7195864.jpg', 1),
(6, 'img/pexels-iris-35972950.jpg', 2);


INSERT INTO enquiries
(buyer_id, property_id, subject, message)

VALUES

(5, 1, 'Room availability', 'Is the room still available?'),

(5, 3, 'Inspection request', 'Can I schedule an inspection this weekend?'),

(6, 8, 'Utilities question', 'Are utilities included in rent?'),

(6, 11, 'Parking question', 'Is parking available nearby?'),

(5, 15, 'Pet policy', 'Are pets allowed in this apartment?');