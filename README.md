# Inventory-Optimization-2-
## 1. Executive Summary
Inventory Optimization for Perishable Retail Products
### Objective: 
Reduce inventory holding cost while maintaining target service level.
### Approach:
- Dynamic demand forecasting.
- Dynamic ROP & TSL.
- Python-based inventory simulation.
### Key results:
- Service Level: 97%.
- Inventory Cost Rate: 1.22%
- Expiry Rate: 0.01%
- Inventory Coverage maintained below shelf life.
  
| Criteria | Target | Result |
| ----------- | --------- | ---------- |
| Service Level     | > 95% | 97% |
| Expiry Rate      | <0.5% | 0.01% |
| Inventory Cost Rate      | <2.00% | 1.22% |
| Inventory Position Coverage < Shelf Life     | Yes | Yes |


<img width="763" height="431" alt="image" src="https://github.com/user-attachments/assets/8fe91e16-5fcd-420d-99fe-53983057ec78" />

## 2. Business Context
#### In retail chain business, inventory is a big section of current assets, it also is a root cause of operation efficiency if it is not managed effectively.
#### Before project, inventory is ordered based on:
   - Fixed inventory level.
   - Order cycle did not adequately reflect fluctuations in customer demand.
#### This led to two major issues:
- Excess Inventory: Capital is hold on inventory, increasing inventory cost and risk of expiry.
- Shortage of goods: Decrease service level, loss of revenue

### A. Project Goal
#### Build a model aimed at:
1. Optimizing inventory level in specific SKU.
2. Maintain Service Level target.
3. Decrease current capital hold on inventory
4. Standardizing the order processes based on data
### B. Solutions 
This project uses a inventory periodic review method:
- Dynamic Reorder Point (ROP).
- Dynamic Target Stock Level (TSL)
Trong đó:
- ROP determines when the order is placed.
- TSL determines the optimal inventory level that needs to be replenished.

## 3. Business Assumptions
### Lead Time: 
| Shelf Life Category | Category A | Category B | Category C |
| ----------- | --------- | ---------- |  ---------- |
| 7 day shelf life    | 1 - 2 days | - | -      |
| 14 day shelf life   | 1 - 2 days | - | -     |
| 30 day shelf life      | 1 - 2 days| 2 - 4 days | 4 - 7 days   |

### Supplier Fill Rate:
- Category A: 90 - 100%
- Category B: 75 - 100%
- Category C: 50 - 100%
### Lost sales are assumed when on-hàn inventory smaller than sales.
### Inventory review schedule:
- 7-day shelf life: Monday, Wednesday, Friday
- 14-day shelf life: Monday, Thursday
- 30-day shelf life: Monday, Thursday

## 4. Methodology
### 4.1 Demand Forcasting (SQL)
### a. Objective
Estimate expected demand for each SKU-store combination on future review periods.
### b. Forecast Logic
<img width="573" height="43" alt="image" src="https://github.com/user-attachments/assets/3ad6bbc5-4628-4c68-8f2e-d62b4b267e11" />

Where: 
- Rolling30D Average: Average sales of the most recent 30 days. 
- Seasonality Index: Day-of-week sales pattern 
- MAE: Historical forecast error. 
- Z: Safety factor configured by category. 
### 4.2 Dynamic Replenishment Policy
### a. Objective
Determine when to place an order and how much inventory should be replenished.
The replenishment model follows a Periodic Review Order-Up-To Policy.
### b. Inventory Position
Inventory decisions are based on Inventory Position rather than physical inventory.

<img width="1075" height="64" alt="image" src="https://github.com/user-attachments/assets/20c06409-8832-4c1f-93be-482ac6b522d8" />

### c. Review Schedule
Different review frequencies are applied based on product shelf life. More frequent reviews are used for shorter-life products to reduce expiry risk.

<img width="609" height="140" alt="image" src="https://github.com/user-attachments/assets/4a878926-9e61-4bf2-a609-eb01b85100b0" />

### d. Calculate TSL & ROP
#### Reorder Point (ROP)
ROP represents the minimum inventory required to cover expected demand during the protection period.
#### Target Stock Level (TSL)
TSL defines the desired inventory position after replenishment, this cover protection period and next review cycle
#### ROP & TSL is calculated by following method:
To prevent future data leakage, the model only uses forecast values generated from information available at the time of calculation. When the protection period extends beyond the available forecast horizon, day-of-week demand patterns are repeated cyclically (D0 → D1 → ... → D6 → D0 → D1 ...), ensuring that replenishment decisions remain realistic and deployable in a production environment.

<img width="1693" height="929" alt="image" src="https://github.com/user-attachments/assets/91d7ba87-fc5e-4183-9a70-986290a3d055" />


### e. Order Trigger
An order is generated only during review date. This replenishes inventory back to the target level while avoiding overstocking.
<img width="539" height="128" alt="image" src="https://github.com/user-attachments/assets/5a8d820e-a5fb-4e27-bf23-e364ead44513" />

### 4.3 Inventory simulation (Python)
### a. Objective
Evaluate replenishment performance under realistic operating conditions.
### b. Simulation inputs
The simulation uses:
- Historical sales data.
- Forecasted demand
- ROP values.
- TSL values
- Product shelf life
- Supplier lead time
### c. Daily inventory update:
For each simulated day:
#### Step 1: Update on-hand inventory
- Deduct previous day's sales, remove expired inventory batches and receive incoming purchase order
- Remove expired inventory batches.
- Receive incoming purchase order (if order arrival date equals current date)
#### Step 2: Calculate Inventory Position
<img width="1075" height="64" alt="image" src="https://github.com/user-attachments/assets/d5ac45e8-e451-4528-892e-43ca69f3de56" />

#### Step 3: Executive inventory review
If current day is a scheduled review date:
- Check ROP
- Generate replenishment order if required
- Schedule future delivery





## II. Method of implementation
<img width="931" height="536" alt="Project Diagram" src="https://github.com/user-attachments/assets/d2edc24a-99ca-4ec8-9b7d-55939c2c719d" />

### Dataset Size
- 5 Year History Sales Data with 913.000 records.
- 10 Stores.
- 50 Items.
- Simulate inventory review process in last year sales data with 182.000 records.
### 1. Calculate Forcasted Demand in SQL
- Using SQL to calculate forecasted demand for each day of the upcoming week.
- Forecasted Demand calculatd by:
  Rolling_30d_average * Seasonality Index + Z * MAE \
  Rolling_30d_average : the average demand of the most 30 days. \
  Seasonality Index: The proportion of sales by day of the week compared to the weekly average.
### 2. Simulate processes of inventory review by Python.
  - Update inventory statement after deducting last sales and expiry batch. Add new inventory batch, if order arrivals.
  - Update Inventory Position.
  - inventory review date is Monday and Thursday for 14 and 30 shelf life day item. Monday, Wednesday and Friday is 7 shelf life item.
  - In inventory review date, if Inventory Position equals or belows ROP, implement calculating TSL - ROP and Order Quantity for next period.
  -  TSL will be calculated to cover R + R + Leadtime (R is the number of days to Next inventory review dates)
  -  ROP will be calculated to cover R + Leadtime.
