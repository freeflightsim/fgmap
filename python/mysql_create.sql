
drop table if exists airwayintersection;
drop table if exists airwaysegment;
drop table if exists apt;
drop table if exists atcfreq;
drop table if exists dme;
drop table if exists dmeils;
drop table if exists fix;
drop table if exists gs;
drop table if exists helipad;
drop table if exists ils;
drop table if exists marker;
drop table if exists ndb;
drop table if exists runwaythreshold;
drop table if exists startuplocation;
drop table if exists vor;


CREATE TABLE airwayintersection (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    name character(5)
);


CREATE TABLE airwaysegment (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    segment_name character(6),
    point1_name character(5),
    point2_name character(5),
    is_high numeric(1,0),
    base_fl numeric(3,0),
    top_fl numeric(3,0)
);


CREATE TABLE apt (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    apt_icao character(4),
    apt_name character(38),
    elevation_m numeric(8,2),
    has_tower numeric(1,0),
    hgt_tower_m numeric(8,2),
    tower_name character(32)
);


CREATE TABLE atcfreq (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    apt_icao character(4),
    atc_type character(4),
    freq_name character(32),
    freq_mhz numeric(7,3)
);


CREATE TABLE dme (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    navaid_id character(4),
    navaid_name character(31),
    subtype character(10),
    elevation_m numeric(8,2),
    freq_mhz numeric(7,3),
    range_km numeric(7,3),
    bias_km numeric(6,2)
);

CREATE TABLE dmeils (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    navaid_id character(4),
    apt_icao character(4),
    rwy_num character(3),
    elevation_m numeric(8,2),
    freq_mhz numeric(7,3),
    range_km numeric(7,3),
    bias_km numeric(6,2)
);


CREATE TABLE fix (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    fix_name character(5)
);


CREATE TABLE gs (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    navaid_id character(4),
    apt_icao character(4),
    rwy_num character(3),
    elevation_m numeric(8,2),
    freq_mhz numeric(7,3),
    range_km numeric(7,3),
    true_heading_deg numeric(6,2),
    glide_slope numeric(6,2)
);

CREATE TABLE helipad (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    apt_icao character(4),
    helipad_name character(5),
    true_heading_deg numeric(6,2),
    length_m double precision,
    width_m double precision,
    surface character(10),
    markings character(22),
    shoulder character(8),
    smoothness numeric(4,2),
    edge_lighting character(4)
);



CREATE TABLE ils (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    navaid_id character(4),
    apt_icao character(4),
    rwy_num character(3),
    subtype character(10),
    elevation_m numeric(8,2),
    freq_mhz numeric(7,3),
    range_km numeric(7,3),
    true_heading_deg numeric(6,2)
);



CREATE TABLE marker (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    apt_icao character(4),
    rwy_num character(3),
    subtype character(10),
    elevation_m numeric(8,2),
    true_heading_deg numeric(6,2)
);



CREATE TABLE ndb (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    navaid_id character(4),
    navaid_name character(32),
    subtype character(10),
    elevation_m numeric(8,2),
    freq_khz numeric(7,3),
    range_km numeric(7,3)
);



CREATE TABLE runwaythreshold (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    apt_icao character(4),
    rwy_num character(3),
    width_m double precision,
    surface character(11),
    shoulder character(8),
    smoothness numeric(4,2),
    centerline_lights numeric(1,0),
    edge_lighting character(4),
    distance_remaining_signs numeric(1,0),
    displaced_threshold_m double precision,
    is_displaced numeric(1,0),
    stopway_length_m double precision,
    markings character(22),
    approach_lighting character(26),
    touchdown_lights numeric(1,0),
    reil character(16),
    length_m double precision,
    true_heading_deg numeric(6,2)
);


CREATE TABLE startuplocation (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    apt_icao character(4),
    name character(38),
    true_heading_deg numeric(6,2)
);



CREATE TABLE vor (
    ogc_fid integer NOT NULL,
    wkb_geometry geometry,
    navaid_id character(4),
    navaid_name character(29),
    subtype character(10),
    elevation_m numeric(8,2),
    freq_mhz numeric(7,3),
    range_km numeric(7,3),
    slaved_variation_deg numeric(6,2)
);


