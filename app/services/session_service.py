from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession
from datetime import datetime

from app.db_models.domain import (
    Session as SessionModel, Frame, Prediction,
    SessionPrediction, Message
)
from app.schemas.session import MessageCreateRequest

def get_user_session_or_404(db: DBSession, session_id: str, person_id: str) -> SessionModel:
    """Ensures the session exists AND belongs to the current user."""
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.person_id == person_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or unauthorized")
    return session

def create_new_session(db: DBSession, person_id: str) -> SessionModel:
    session = SessionModel(person_id=person_id, status="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def update_session_status(db: DBSession, session_id: str, person_id: str, new_status: str):
    session = get_user_session_or_404(db, session_id, person_id)
    session.status = new_status
    db.commit()
    return {"status": "updated"}



def calculate_session_summary(db: DBSession, session_id: str, person_id: str):
    get_user_session_or_404(db, session_id, person_id)

    # Prevent duplicate summaries
    db.query(SessionPrediction).filter(SessionPrediction.session_id == session_id).delete()

    results = []
    for model_type in ["optical", "thermal"]:
        frames = db.query(Frame).filter(
            Frame.session_id == session_id,
            Frame.camera_type == model_type
        ).all()
        frame_ids = [f.frame_id for f in frames]

        if not frame_ids:
            continue

        predictions = db.query(Prediction).filter(Prediction.frame_id.in_(frame_ids)).all()
        if not predictions:
            continue

        probs = [p.stress_probability for p in predictions]
        sp = SessionPrediction(
            session_id=session_id,
            model_type=model_type,
            avg_stress_probability=sum(probs) / len(probs),
            max_stress_probability=max(probs),
        )
        db.add(sp)
        results.append({
            "model_type": model_type,
            "avg": sp.avg_stress_probability,
            "max": sp.max_stress_probability,
        })

    db.commit()
    return {"summaries": results}

def get_user_statistics(db: DBSession, person_id: str):
    sessions = db.query(SessionModel).filter(SessionModel.person_id == person_id).all()
    
    total_sessions = len(sessions)
    if total_sessions == 0:
        return {
            "total_sessions": 0,
            "avg_stress": 0,
            "status": "No data",
            "latest_session_date": None
        }
    
    session_ids = [s.session_id for s in sessions]
    predictions = db.query(SessionPrediction).filter(SessionPrediction.session_id.in_(session_ids)).all()
    
    avg_stress = 0
    if predictions:
        avg_stress = (sum([p.avg_stress_probability for p in predictions]) / len(predictions)) * 100
    
    status = "Low"
    if avg_stress > 70: status = "High"
    elif avg_stress > 40: status = "Medium"
    
    latest_session = max(sessions, key=lambda s: s.created_at)
    
    return {
        "total_sessions": total_sessions,
        "avg_stress": round(avg_stress, 1),
        "status": status,
        "latest_session_date": latest_session.created_at,
    }

def save_chat_message(db: DBSession, session_id: str, person_id: str, request: MessageCreateRequest):
    get_user_session_or_404(db, session_id, person_id)

    message = Message(
        session_id=session_id,
        role=request.role,
        content=request.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_chat_history(db: DBSession, session_id: str, person_id: str):
    get_user_session_or_404(db, session_id, person_id)
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp.asc()).all()

def get_user_history(db: DBSession, person_id: str):
    sessions = db.query(SessionModel).filter(
        SessionModel.person_id == person_id,
        SessionModel.status == "completed"
    ).order_by(SessionModel.created_at.desc()).all()

    history = []
    for s in sessions:
        predictions = db.query(SessionPrediction).filter(SessionPrediction.session_id == s.session_id).all()
        avg_optical = next((p.avg_stress_probability for p in predictions if p.model_type == "optical"), None)
        avg_thermal = next((p.avg_stress_probability for p in predictions if p.model_type == "thermal"), None)
        
        history.append({
            "session_id": s.session_id,
            "created_at": s.created_at,
            "status": s.status,
            "avg_optical_stress": avg_optical,
            "avg_thermal_stress": avg_thermal,
        })
    return history

def get_session_details(db: DBSession, session_id: str, person_id: str):
    session = get_user_session_or_404(db, session_id, person_id)
    
    optical_data = []
    thermal_data = []
    
    frames = db.query(Frame).filter(Frame.session_id == session_id).order_by(Frame.timestamp.asc()).all()
    if frames:
        frame_ids = [f.frame_id for f in frames]
        predictions = db.query(Prediction).filter(Prediction.frame_id.in_(frame_ids)).all()
        pred_map = {p.frame_id: p for p in predictions}
        
        for f in frames:
            p = pred_map.get(f.frame_id)
            if p:
                point = {
                    "timestamp": int(f.timestamp.timestamp() * 1000),
                    "score": round(p.stress_probability * 100) if f.camera_type == "optical" else None,
                    "prob": p.stress_probability if f.camera_type == "thermal" else None,
                    "status": "FACE_DETECTED"
                }
                if f.camera_type == "optical":
                    optical_data.append(point)
                else:
                    thermal_data.append(point)
                    
    messages = get_chat_history(db, session_id, person_id)
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "optical": optical_data,
        "thermal": thermal_data,
        "messages": messages
    }