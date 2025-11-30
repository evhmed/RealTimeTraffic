# Real-Time Traffic Data Pipeline on Azure

A fully automated **real-time data engineering pipeline** built on Microsoft Azure.

## Architecture Overview
Azure Maps → Function App → Event Hubs → Stream Analytics → Power BI  
                           SQL Database → Future ML Model


## Project Description

This project features a real-time traffic monitoring system that streams traffic events from Azure Maps and processes them across Azure cloud services. It supports:

- Real-time event streaming  
- Automated ETL processing  
- Structured storage for historical insights  
- Live Power BI dashboard visualization  
- ML-ready data architecture  


## Objectives

- Collect and process live traffic data in real time  
- Store normalized data in Azure SQL  
- Build interactive Power BI dashboards  
- Ensure high throughput, low latency pipeline  
- Prepare foundation for predictive analytics  


## Tools and Technologies

| Tool / Service | Purpose |
|----------------|---------|
| Azure Maps | Fetch live incident data |
| Azure Function App | API calls and ingestion |
| Event Hubs | Streaming event ingestion |
| Stream Analytics | Real-time transformation |
| Azure SQL Database | Persistent historical storage |
| Power BI | Monitoring dashboard |
| Python | Data scripts |
| SQL | Database operations |
| Log Analytics | Pipeline monitoring |


## Stakeholders and Benefits

| Stakeholder | Value |
|-------------|--------|
| Traffic Authorities | Live dashboard for road monitoring |
| Drivers | Reduced delays via optimized flow |
| Ministry of Transport | Data-driven infrastructure planning |
| Researchers | Clean, continuous dataset for ML models |
| Government Decision Makers | Strategic mobility insights |


## Database Design

### Database: TrafficSQL  
### Table: TrafficData

| Field | Type | Description |
|-------|------|-------------|
| city | VARCHAR | Event city |
| latitude | FLOAT | Latitude |
| longitude | FLOAT | Longitude |
| description | NVARCHAR | Incident description |
| incident_count | INT | Total incidents computed per window |
| timestamp | DATETIME | Event timestamp |
| window_end | DATETIME | Aggregation window end |

### Design Logic

- Stream Analytics aggregates events coming from Event Hubs  
- Each processed window is stored in SQL  
- Power BI consumes SQL for live visuals and trend analysis  


## Power BI Dashboard Design

### Dashboard Sections

- Live map of traffic incidents  
- KPIs: total incidents, severe cases, jam counts  
- Line charts for incident frequency  
- Bar charts comparing cities  
- Gauge for accident likelihood  
- Table view with recent events  

### UX Principles

- Clean minimal design  
- Real-time data refresh  
- Interactive filtering  
- Future scalability for ML integration  


## Deployment Steps (High-Level)

1. Create Azure Maps account  
2. Deploy Function App to pull traffic API data  
3. Create Event Hub to ingest streamed payloads  
4. Create Stream Analytics Job  
   - Input: Event Hub  
   - Output: SQL Database and Power BI  
5. Create SQL Database with TrafficData schema  
6. Publish dashboard in Power BI 


## Future Enhancements

- Predictive modeling for congestion  
- Incident anomaly detection  
- Weather and IoT sensor integration  
- Mobile alert system for drivers
