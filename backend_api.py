from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import databases
import sqlalchemy

# DATABASE CONNECTION CONFIGURATION
# Note: Replace 'root' and 'password' with your real SQL username and password
DATABASE_URL = "mysql+aiomysql://root:password@localhost:3306/maintenance_management_db"
DATABASE_URL = "mysql+aiomysql://root:1234@localhost:3306/maintenance_management_db"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI(title="Computerized Maintenance Management System (CMMS) APIs")

# REQUEST & RESPONSE VALIDATION SCHEMA MODELS
class BreakdownTicketRaise(BaseModel):
    machine_number: str
    problem_type: str
    operator_code: str

class TicketUpdateSchema(BaseModel):
    technician_name: str
    action_taken: str
    reason: str
    status: str  # 'In Progress' or 'Closed'

class StoreIssueSchema(BaseModel):
    part_no: str
    issue_qty: int

class PedAnalysisSchema(BaseModel):
    ticket_no: int
    why_1: str
    why_2: str
    why_3: str
    why_4: str
    why_5: str
    root_cause: str
    capa_action: str
from contextlib import asynccontextmanager
# MODERN LIFESPAN EVENT HANDLER REGISTER
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup: Database connect karein
    await database.connect()
    yield
    # Application shutdown: Database disconnect karein
    await database.disconnect()

# UPDATE THIS LINE (Line jahan app = FastAPI() likha hai)
app = FastAPI(
    title="Computerized Maintenance Management System (CMMS) APIs",
    lifespan=lifespan
)
# MODULE 1: OPERATOR BREAKDOWN ENTRY & AUTO TICKET
@app.post("/api/tickets/raise", response_model=dict)
async def raise_breakdown_ticket(ticket: BreakdownTicketRaise):
    # Verify if machine asset profile structure exists
    machine_query = "SELECT * FROM machine_master WHERE machine_number = :m_num"
    machine = await database.fetch_one(query=machine_query, values={"m_num": ticket.machine_number})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine number asset not found in master register database.")

    # Core insertion query logs data metrics variables
    query = """
        INSERT INTO tickets (machine_number, problem_type, operator_code, auto_start_time, status)
        VALUES (:machine_number, :problem_type, :operator_code, :start_time, 'Open')
    """
    values = {
        "machine_number": ticket.machine_number,
        "problem_type": ticket.problem_type,
        "operator_code": ticket.operator_code,
        "start_time": datetime.now()
    }
    
    last_record_id = await database.execute(query=query, values=values)
    
    # Auto-generate dynamic ticket format string token allocation
    generated_ticket_no = f"TKT-{last_record_id}"
    return {
        "status": "Success",
        "message": f"Breakdown tracking ticket successfully opened.",
        "ticket_id": last_record_id,
        "auto_ticket_no": generated_ticket_no
    }

# MODULE 2: MAINTENANCE WORKFLOW ENGINE & AUTOMATED MTTR EVALUATION
@app.put("/api/tickets/update/{ticket_no}", response_model=dict)
async def update_maintenance_ticket(ticket_no: int, payload: TicketUpdateSchema):
    # Retrieve base ticket context timeline records logs parameters
    select_query = "SELECT auto_start_time FROM tickets WHERE ticket_no = :t_no"
    ticket_record = await database.fetch_one(query=select_query, values={"t_no": ticket_no})
    if not ticket_record:
        raise HTTPException(status_code=404, detail="Requested ticket record allocation code missing.")
    
    stop_time = None
    calculated_mttr = 0
    
    # Core automated calculation evaluation routines if closing logs context states
    if payload.status == "Closed":
        stop_time = datetime.now()
        start_time = ticket_record["auto_start_time"]
        time_diff = stop_time - start_time
        calculated_mttr = int(time_diff.total_seconds() / 60) # Converted to minute metrics scalar integers

    update_query = """
        UPDATE tickets 
        SET technician_name = :tech_name, action_taken = :action, reason = :reason, 
            status = :status, auto_stop_time = :stop_time, mttr_minutes = :mttr
        WHERE ticket_no = :t_no
    """
    values = {
        "tech_name": payload.technician_name,
        "action": payload.action_taken,
        "reason": payload.reason,
        "status": payload.status,
        "stop_time": stop_time,
        "mttr": calculated_mttr,
        "t_no": ticket_no
    }
    
    await database.execute(query=update_query, values=values)
    return {
        "status": "Updated",
        "ticket_no": ticket_no,
        "current_state": payload.status,
        "calculated_mttr_minutes": calculated_mttr
    }

# MODULE 3: STORE LEDGER TRANSACTION MANAGEMENT
@app.post("/api/store/issue")
async def issue_inventory_spares(payload: StoreIssueSchema):
    part_query = "SELECT stock, cost FROM spare_parts_master WHERE part_no = :p_no"
    part = await database.fetch_one(query=part_query, values={"p_no": payload.part_no})
    if not part:
        raise HTTPException(status_code=404, detail="Spare part specification index not registered in warehouses logs.")
        
    if part["stock"] < payload.issue_qty:
        raise HTTPException(status_code=400, detail="Insufficient stock availability for extraction allocation profiles.")
        
    # Process inventory balances arrays
    new_stock = part["stock"] - payload.issue_qty
    total_cost = float(part["cost"]) * payload.issue_qty
    
    update_stock_query = "UPDATE spare_parts_master SET stock = :n_stock WHERE part_no = :p_no"
    await database.execute(query=update_stock_query, values={"n_stock": new_stock, "p_no": payload.part_no})
    
    return {
        "status": "Issued",
        "part_no": payload.part_no,
        "remaining_stock": new_stock,
        "transaction_cost_evaluated": total_cost
    }

# MODULE 4: LIVE DASHBOARD METRICS CALCULATION (KPI METRICS GENERATOR)
@app.get("/api/dashboard/metrics")
async def generate_dashboard_metrics():
    open_bd = await database.fetch_val(query="SELECT COUNT(*) FROM tickets WHERE status = 'Open'")
    closed_bd = await database.fetch_val(query="SELECT COUNT(*) FROM tickets WHERE status = 'Closed'")
    avg_mttr = await database.fetch_val(query="SELECT AVG(mttr_minutes) FROM tickets WHERE status = 'Closed'") or 0
    
    # OEE Context dummy estimation baseline (Can be mapped dynamically with dynamic machines registers runtime arrays logs)
    calculated_oee = 85.5 
    
    return {
        "live_status": "Active Operational Engine State",
        "counters": {
            "open_breakdowns": open_bd,
            "closed_breakdowns": closed_bd,
            "mean_time_to_repair_minutes": round(float(avg_mttr), 2)
        },
        "performance_analytics": {
            "overall_equipment_effectiveness_oee": f"{calculated_oee}%",
            "mtbf_hours_estimation": "72.4 Hours"
        }
    }
