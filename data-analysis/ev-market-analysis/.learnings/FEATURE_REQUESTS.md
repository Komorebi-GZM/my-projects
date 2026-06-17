# Feature Requests

Capabilities requested by the user.

---

## [FEAT-20260505-001] analysis_direction

**Logged**: 2026-05-05T12:00:00Z
**Priority**: medium
**Status**: pending
**Area**: backend

### Requested Capability
User wants to determine analysis direction after data cleaning is complete. The project currently only has ch01 (data cleaning). Additional analysis chapters need to be planned based on cleaned data characteristics.

### User Context
User stated "先清洗，根据结果再看" (clean first, decide analysis direction based on results). Now that cleaning is complete with 1070 rows x 27 columns, the next step is to propose analysis directions.

### Complexity Estimate
medium

### Suggested Implementation
Potential analysis directions based on data characteristics:
1. Brand competitiveness analysis (price, performance, sales comparison)
2. Market segment profiling (Budget vs Mid-range vs Premium vs Luxury)
3. Country-of-origin comparison (US vs China vs Germany vs Japan vs South Korea)
4. Price-performance correlation analysis
5. EV technology trend analysis (battery capacity, range, charging speed over years)
6. Sales driver analysis (what factors most influence annual_sales_units)

### Metadata
- Frequency: first_time
- Related Features: ch01_data_cleaning
