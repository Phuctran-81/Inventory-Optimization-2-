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
### Lost sales are assumed when on-hand inventory smaller than sales.
### Inventory review schedule:
- 7-day shelf life: Monday, Wednesday, Friday
- 14-day shelf life: Monday, Thursday
- 30-day shelf life: Monday, Thursday

### Dataset Size
- 5 Year History Sales Data with 913.000 records.
- 10 Stores.
- 50 Items.
- Simulate inventory review process in last year sales data with 182.000 records.

## 4. Methodology
### 4.1 Demand Forcasting (SQL)
### a. Objective
Estimate expected demand for each SKU-store combination on future review periods.
### b. Forecast Logic
<img width="727" height="54" alt="image" src="https://github.com/user-attachments/assets/d9669178-5cd5-46e6-baa7-de7b14830144" />


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

<img width="676" height="43" alt="image" src="https://github.com/user-attachments/assets/27722cc5-ac64-4eb9-9900-c650518047b8" />

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
<img width="626" height="154" alt="image" src="https://github.com/user-attachments/assets/76af0e89-489f-40ef-99a2-dac7dc4d60b3" />


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
<img width="676" height="43" alt="image" src="https://github.com/user-attachments/assets/27722cc5-ac64-4eb9-9900-c650518047b8" />


#### Step 3: Executive inventory review
If current day is a scheduled review date:
- Check ROP
- Generate replenishment order if required
- Schedule future delivery


## 5. Architecture Diagram
### 5.1 End-to-End Data Pipeline Architecture

<img width="9310" height="4560" alt="Project Diagram" src="https://github.com/user-attachments/assets/2814ff3e-3d6c-4740-b110-5894dc7069af" />


### 5.2 Inventory Optimization Architecture

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/cd759cdb-f933-4f7d-9eff-e294616ca72a" />


