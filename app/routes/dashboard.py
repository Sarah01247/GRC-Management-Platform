from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.core.dependencies import get_current_user
from app.database.connection import get_db
from datetime import datetime
from reportlab.platypus import Table, TableStyle
from app.models.organization import Organization
from app.models.framework import Framework
from app.models.control import Control
from app.models.risk import Risk
from app.models.control_assessment import ControlAssessment
from collections import defaultdict
from app.models.audit_log import AuditLog
from openpyxl.styles import Font
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)



def generate_risk_recommendations(risk_title):

    if not risk_title:
        return []


    title = risk_title.lower()


    if "data" in title or "leakage" in title:

        return [
            "Enable Data Loss Prevention (DLP)",
            "Review access permissions",
            "Encrypt sensitive data",
            "Perform periodic access audits"
        ]


    elif "access" in title or "authentication" in title:

        return [
            "Enable Multi-Factor Authentication (MFA)",
            "Review user privileges",
            "Apply least privilege principle",
            "Monitor authentication logs"
        ]


    elif "network" in title:

        return [
            "Review firewall rules",
            "Perform network segmentation",
            "Monitor network traffic",
            "Update security configurations"
        ]


    return [
        "Review existing controls",
        "Perform risk assessment",
        "Implement mitigation plan",
        "Monitor risk status"
    ]





def calculate_security_score(
    compliance,
    critical_risks,
    evidence_coverage,
    control_implementation
):

    risk_score = 100


    if critical_risks > 0:
        risk_score = 40


    score = (

        (compliance * 0.4)

        +

        (risk_score * 0.3)

        +

        (evidence_coverage * 0.2)

        +

        (control_implementation * 0.1)

    )


    return round(score, 2)





def get_security_rating(score):

    if score >= 90:
        return "Excellent"

    elif score >= 75:
        return "Good"

    elif score >= 50:
        return "Needs Improvement"

    else:
        return "Poor"





@router.get("/overview")
def get_dashboard_overview(
    organization_id: int | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if organization_id:

        organization = db.query(Organization).filter(
            Organization.organization_id == organization_id
        ).first()

        frameworks = db.query(Framework).filter(
            Framework.organization_id == organization_id
        ).all()

        controls = db.query(Control).join(
            Framework
        ).filter(
            Framework.organization_id == organization_id
        ).all()

        risks = db.query(Risk).filter(
            Risk.organization_id == organization_id
        ).all()

    else:

        organization = None
        frameworks = db.query(Framework).all()
        controls = db.query(Control).all()
        risks = db.query(Risk).all()



    critical = 0
    high = 0
    medium = 0
    low = 0

    risk_details = {}

    risk_map = {}

    top_risk = None
    highest_score = 0


    for risk in risks:

        score = risk.likelihood * risk.impact

        if score >= 16:
             severity = "Critical"

        elif score >= 11:
           severity = "High"

        elif score >= 6:
             severity = "Medium"

        else:
            severity = "Low"


        if risk.title not in risk_map:

            risk_map[risk.title] = {
            "title": risk.title,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
            "score": score,
            "severity": severity,
            "treatment_status": risk.status
        }


        elif score > risk_map[risk.title]["score"]:

            risk_map[risk.title]["likelihood"] = risk.likelihood
            risk_map[risk.title]["impact"] = risk.impact
            risk_map[risk.title]["score"] = score
            risk_map[risk.title]["severity"] = severity
            risk_map[risk.title]["treatment_status"] = risk.status


        if risk.title in risk_details:
            risk_details[risk.title] += 1
        else:
             risk_details[risk.title] = 1


        if score <= 5:
           low += 1

        elif score <= 10:
            medium += 1

        elif score <= 15:
            high += 1

        else:
              critical += 1


        if score > highest_score:
            highest_score = score
            top_risk = risk.title

    risk_list = list(risk_map.values())


    control_ids = [
    control.control_id
    for control in controls
]


    if control_ids:

        implemented = db.query(
        ControlAssessment.control_id
    ).filter(
        ControlAssessment.control_id.in_(control_ids),
        ControlAssessment.status == "Implemented"
    ).distinct().count()

    else:

        implemented = 0


    print("CONTROL IDS =", control_ids)

    test_assessments = db.query(ControlAssessment).all()

    print("TOTAL ASSESSMENTS =", len(test_assessments))

    for a in test_assessments:
         print(
        "ASSESSMENT =>",
        a.assessment_id,
        a.control_id,
        a.status
    )


    if len(controls) > 0:

        compliance = round(
        (implemented / len(controls)) * 100,
        2
    )

        control_implementation = (
        implemented / len(controls)
    ) * 100

    else:

         compliance = 0
         control_implementation = 0


    evidence_controls = 0


    for control in controls:

        if len(control.evidences) > 0:
              evidence_controls += 1


    if len(controls) > 0:

         evidence_coverage = (
        evidence_controls / len(controls)
    ) * 100

    else:

        evidence_coverage = 0
    security_score = calculate_security_score(
        compliance,
        critical,
        evidence_coverage,
        control_implementation
    )


    security_rating = get_security_rating(
            security_score
        )

    audit_logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).all()


    audit_summary = {

        "total_actions": len(audit_logs),

        "create_actions": len([
            log for log in audit_logs
            if log.action == "CREATE"
        ]),

        "update_actions": len([
            log for log in audit_logs
            if log.action == "UPDATE"
        ]),

        "delete_actions": len([
            log for log in audit_logs
            if log.action == "DELETE"
        ]),

        "latest_activity": None

    }


    if audit_logs:

        latest = audit_logs[0]

        audit_summary["latest_activity"] = {

            "user": (
                latest.user.username
                if latest.user
                else None
            ),

            "action": latest.action,

            "entity": latest.entity,

            "description": latest.description

        }
    return {

        "organization": (
            organization.name
            if organization
            else "All Organizations"
        ),


        "security_posture": {

            "compliance_score": compliance,

            "security_score": security_score,

            "security_rating": security_rating,

            "risk_level": (
                "Critical"
                if critical > 0
                else "Normal"
            )

        },


        "frameworks": [
            framework.name
            for framework in frameworks
        ],


        "controls": {

            "total": len(controls),

            "implemented": implemented

        },


        "risks": {

            "total": len(risks),

            "critical": critical,

            "high": high,

            "medium": medium,

            "low": low

        },


        "top_risk": top_risk,


        "risk_list": risk_list,


        "risk_details": risk_details,


        "risk_treatment": {

            "risk": top_risk,

            "recommendations":
                generate_risk_recommendations(top_risk)

        },


        "audit_summary": audit_summary

    }









@router.get("/report")
def get_dashboard_report(
    organization_id: int | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    overview = get_dashboard_overview(
        organization_id,
        user,
        db
    )

    security = overview["security_posture"]
    risks = overview["risks"]
    top_risk = overview["top_risk"]

    findings = []

    if risks["critical"] > 0:
        findings.append(
            f"{risks['critical']} Critical Risks Identified"
        )

    if top_risk:
        findings.append(
            f"Highest Risk: {top_risk}"
        )

    if security["compliance_score"] < 80:
        findings.append(
            "Compliance level requires improvement"
        )
    else:
        findings.append(
            "Compliance level is acceptable"
        )


    return {
        "report_title":
            f"{overview['organization']} Security Assessment Report",

        "summary":
            f"{overview['organization']} achieved a security score of {security['security_score']}%.",

        "security_score":
            security["security_score"],

        "security_rating":
            security["security_rating"],

        "risk_level":
            security["risk_level"],

        "main_findings":
            findings,

        "recommended_actions":
            generate_risk_recommendations(top_risk),

        "risk_details":
            overview["risk_details"],

        "risk_list":
            overview["risk_list"],

        "controls":
            overview["controls"],

        "compliance_score":
            overview["security_posture"]["compliance_score"],

        "audit_summary":
            overview["audit_summary"]
    }

@router.get("/report/pdf")
def generate_pdf_report(
    organization_id: int | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    report = get_dashboard_report(
    organization_id,
    user,
    db
)
    audit_summary = report.get(
    "audit_summary",
    {}
)
    print(report.keys())


    file_name = "security_assessment_report.pdf"


    doc = SimpleDocTemplate(
        file_name
    )


    styles = getSampleStyleSheet()


    content = []


    content.append(
        Paragraph(
            "GRC Security Assessment Report",
            styles["Title"]
        )
    )


    content.append(
        Spacer(1, 12)
    )


    content.append(
        Paragraph(
            f"Organization: {report['report_title'].replace(' Security Assessment Report', '')}",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            "Framework: ISO 27001",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            "Generated By: GRC Platform",
            styles["Normal"]
        )
    )


    content.append(
        Paragraph(
            f"Report Date: {datetime.now().strftime('%Y-%m-%d')}",
            styles["Normal"]
        )
    )
    content.append(
    Spacer(1, 12)
)


    content.append(
    Paragraph(
        "Assessment Information",
        styles["Heading2"]
    )
)


    assessment_data = [
    [
        "Item",
        "Value"
    ],
    [
        "Report ID",
        "GRC-2026-001"
    ],
    [
        "Assessment Scope",
        "Information Security Controls and Risk Assessment"
    ],
    [
        "Framework Version",
        "ISO 27001:2022"
    ],
    [
        "Generated By",
        "GRC Platform User"
    ]
]


    assessment_table = Table(
    assessment_data
)


    assessment_table.setStyle(
    TableStyle(
        [
            ("GRID", (0,0), (-1,-1), 0.5, None),
            ("ALIGN", (0,0), (-1,-1), "CENTER")
        ]
    )
)


    content.append(
    assessment_table
)

    content.append(
        Spacer(1, 20)
    )

    content.append(
        Paragraph(
            "Security Summary",
            styles["Heading2"]
        )
    )
    

    summary_data = [
        [
            "Metric",
            "Value"
        ],
        [
            "Security Score",
            str(report["security_score"])
        ],
        [
            "Security Rating",
            report["security_rating"]
        ],
        [
            "Risk Level",
            report["risk_level"]
        ]
    ]


    summary_table = Table(
        summary_data
    )


    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0,0), (-1,-1), 0.5, None),
                ("ALIGN", (0,0), (-1,-1), "CENTER")
            ]
        )
    )


    content.append(
        summary_table
    )


    content.append(
        Spacer(1, 12)
    )
    content.append(
        Paragraph(
            "Compliance Overview",
            styles["Heading2"]
        )
    )

    content.append(
        Spacer(1, 12)
    )


   

    compliance_data = [
        [
            "Item",
            "Status"
        ],
        [
            "Framework",
            "ISO 27001"
        ],
        [
            "Control Assessment",
            "Completed"
        ],
        [
            "Risk Assessment",
            "Completed"
        ]
    ]


    compliance_table = Table(
        compliance_data
    )


    compliance_table.setStyle(
        TableStyle(
            [
                ("GRID", (0,0), (-1,-1), 0.5, None),
                ("ALIGN", (0,0), (-1,-1), "CENTER")
            ]
        )
    )


    content.append(
        compliance_table
    )
    content.append(
    Spacer(1, 12)
)


    



    content.append(
        Spacer(1, 12)
    )


    content.append(
        Paragraph(
            report["summary"],
            styles["Normal"]
        )
    )


    content.append(
        Spacer(1, 12)
    )


    


    content.append(
        Spacer(1, 12)
    )


    content.append(
        Paragraph(
            "Main Findings:",
            styles["Heading2"]
        )
    )


    


    for finding in report["main_findings"]:

        content.append(
            Paragraph(
                "- " + finding,
                styles["Normal"]
            )
        )
    content.append(
    Spacer(1, 12)
)


    content.append(
    Paragraph(
        "Recommended Actions:",
        styles["Heading2"]
    )
)


    content.append(
        Spacer(1, 12)
    )


   


    for action in report["recommended_actions"]:

        content.append(
            Paragraph(
                "- " + action,
                styles["Normal"]
            )
        )
        content.append(
        Spacer(1, 12)
    )

    content.append(
    Paragraph(
        "Risk Treatment Summary",
        styles["Heading2"]
    )
)


    treatment_counts = {
    "Open": 0,
    "In Progress": 0,
    "Closed": 0
}


    for risk in report["risk_list"]:
       status = risk["treatment_status"]

       if status in treatment_counts:
        treatment_counts[status] += 1



    treatment_data = [
    [
        "Treatment Status",
        "Count"
    ],
    [
        "Open",
        str(treatment_counts["Open"])
    ],
    [
        "In Progress",
        str(treatment_counts["In Progress"])
    ],
    [
        "Closed",
        str(treatment_counts["Closed"])
    ]
]


    treatment_table = Table(
    treatment_data
)


    treatment_table.setStyle(
    TableStyle(
        [
            ("GRID", (0,0), (-1,-1), 0.5, None),
            ("ALIGN", (0,0), (-1,-1), "CENTER")
        ]
    )
)


    content.append(
    treatment_table
)


    content.append(
    Spacer(1,12)
)
    content.append(
        Paragraph(
            "Risk Register",
            styles["Heading2"]
        )
)


    risk_data = [
    [
        "Risk",
        "Likelihood",
        "Impact",
        "Risk Score",
        "Severity",
        "Treatment"
    ]
]


    for risk in report["risk_list"]:

        risk_data.append(
        [
            risk["title"],
            str(risk["likelihood"]),
            str(risk["impact"]),
            str(risk["score"]),
            risk["severity"],
            risk["treatment_status"]
        ]
    )


    risk_table = Table(
        risk_data
    )


    risk_table.setStyle(
        TableStyle(
            [
                ("GRID", (0,0), (-1,-1), 0.5, None),
                ("ALIGN", (0,0), (-1,-1), "CENTER")
            ]
        )
    )


    content.append(
        risk_table
    )


    content.append(
        Spacer(1, 12)
    )


    content.append(
        Paragraph(
            "Control Compliance",
            styles["Heading2"]
        )
    )


    control_data = [
        [
            "Metric",
            "Value"
        ],
        [
            "Total Controls",
            str(report["controls"]["total"])
        ],
        [
            "Implemented Controls",
            str(report["controls"]["implemented"])
        ],
        [
            "Compliance Rate",
            f"{report['compliance_score']}%"
        ]
    ]


    control_table = Table(
        control_data
    )


    control_table.setStyle(
        TableStyle(
            [
                ("GRID", (0,0), (-1,-1), 0.5, None),
                ("ALIGN", (0,0), (-1,-1), "CENTER")
            ]
        )
    )


    content.append(
        control_table
    )


   

# ... التوصيات هنا


# أضيفي هنا قسم Audit Activity Summary 👇

    content.append(
    Spacer(1, 12)
)


    content.append(
      Paragraph(
        "Audit Activity Summary",
        styles["Heading2"]
    )
)


    audit_table_data = [
    [
        "Metric",
        "Value"
    ],
    [
        "Total Actions",
        str(audit_summary.get("total_actions", 0))
    ],
    [
        "Create Actions",
        str(audit_summary.get("create_actions", 0))
    ],
    [
        "Update Actions",
        str(audit_summary.get("update_actions", 0))
    ],
    [
        "Delete Actions",
        str(audit_summary.get("delete_actions", 0))
    ]
]


    audit_table = Table(
    audit_table_data
)


    audit_table.setStyle(
    TableStyle(
        [
            ("GRID", (0,0), (-1,-1), 0.5, None),
            ("ALIGN", (0,0), (-1,-1), "CENTER")
        ]
    )
)


    content.append(
    audit_table
)


    latest = audit_summary.get("latest_activity")


    if latest:

        content.append(
        Spacer(1, 8)
    )


        content.append(
          Paragraph(
            f"""
            Latest Activity:<br/>
            User: {latest.get('user')}<br/>
            Action: {latest.get('action')}<br/>
            Entity: {latest.get('entity')}<br/>
            Description: {latest.get('description')}
            """,
            styles["Normal"]
        )
    )


    doc.build(content)


    return FileResponse(
    file_name,
    media_type="application/pdf",
    filename=file_name
)
from openpyxl import Workbook
from fastapi.responses import FileResponse

@router.get("/report/excel")
def generate_excel_report(
    organization_id: int | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    report = get_dashboard_report(
        organization_id,
        user,
        db
    )

    file_name = "security_assessment_report.xlsx"

    wb = Workbook()
    # Dashboard Sheet

    dashboard_ws = wb.create_sheet(
    "Dashboard"
)


    dashboard_ws.append(
    ["GRC Security Dashboard"]
)


    dashboard_ws.append(
    [
        "Metric",
        "Value"
    ]
)


    dashboard_ws.append(
    [
        "Security Score",
        report["security_score"]
    ]
)


    dashboard_ws.append(
    [
        "Security Rating",
        report["security_rating"]
    ]
)


    dashboard_ws.append(
    [
        "Risk Level",
        report["risk_level"]
    ]
)


    dashboard_ws.append(
    [
        "Compliance Rate",
        report["compliance_score"]
    ]
)


    dashboard_ws.append(
    []
)


    dashboard_ws.append(
    [
        "Risk Category",
        "Count"
    ]
)


    critical_count = len([
        risk for risk in report["risk_list"]
        if risk["severity"] == "Critical"
])


    high_count = len([
    risk for risk in report["risk_list"]
    if risk["severity"] == "High"
])


    medium_count = len([
    risk for risk in report["risk_list"]
    if risk["severity"] == "Medium"
])


    low_count = len([
    risk for risk in report["risk_list"]
    if risk["severity"] == "Low"
])


    dashboard_ws.append(
[
    "Critical",
    critical_count
]
)


    dashboard_ws.append(
[
    "High",
    high_count
]
)


    dashboard_ws.append(
[
    "Medium",
    medium_count
]
)


    dashboard_ws.append(
[
    "Low",
    low_count
]
)


    dashboard_ws.append(
    [
        "Total Risks",
        len(report["risk_list"])
    ]
)


    dashboard_ws.append(
    [
        "Total Controls",
        report["controls"]["total"]
    ]
)


    dashboard_ws.append(
    [
        "Implemented Controls",
        report["controls"]["implemented"]
    ]
)


    dashboard_ws.append(
    []
)


    dashboard_ws.append(
    [
        "Audit Actions",
        report["audit_summary"]["total_actions"]
    ]
)
    ws = wb.active
    ws.title = "Security Report"
    title_font = Font(
    bold=True,
    size=14
)

    header_font = Font(
    bold=True
)

    center = Alignment(
    horizontal="center"
)
    title_font = Font(
    bold=True,
    size=14
)


    ws.append(
        ["GRC Security Assessment Report"]
    )
    ws["A1"].font = title_font
    ws["A1"].alignment = center
    ws["A1"].font = title_font
    ws.append(
        [
            "Organization",
            report["report_title"].replace(
                " Security Assessment Report",
                ""
            )
        ]
    )

    ws.append(
        [
            "Security Score",
            report["security_score"]
        ]
    )

    ws.append(
        [
            "Security Rating",
            report["security_rating"]
        ]
    )

    ws.append(
        [
            "Risk Level",
            report["risk_level"]
        ]
    )

    ws.append(
        [
            "Compliance Rate",
            report["compliance_score"]
        ]
    )


    ws.append([])


    # Risk Register

    ws.append(
        [
            "Risk",
            "Likelihood",
            "Impact",
            "Score",
            "Severity",
            "Treatment"
        ]
    )
    for cell in ws[8]:
        cell.font = header_font
        cell.alignment = center
    for cell in ws[8]:
       cell.font = Font(bold=True)


    for risk in report["risk_list"]:

        ws.append(
            [
                risk["title"],
                risk["likelihood"],
                risk["impact"],
                risk["score"],
                risk["severity"],
                risk["treatment_status"]
            ]
        )
        
    severity_cell = ws.cell(
        row=ws.max_row,
        column=5
    )

    if risk["severity"] == "Critical":
        severity_cell.fill = PatternFill(
            "solid",
            fgColor="FF0000"
        )

    elif risk["severity"] == "High":
        severity_cell.fill = PatternFill(
            "solid",
            fgColor="FFA500"
        )

    elif risk["severity"] == "Medium":
        severity_cell.fill = PatternFill(
            "solid",
            fgColor="FFFF00"
        )


    ws.append([])


    # Audit Activity Summary

    ws.append(
        [
            "Audit Activity Summary"
        ]
    )
    ws["A12"].font = Font(bold=True)

    audit = report.get(
        "audit_summary",
        {}
    )


    ws.append(
        [
            "Total Actions",
            audit.get("total_actions", 0)
        ]
    )


    ws.append(
        [
            "Create Actions",
            audit.get("create_actions", 0)
        ]
    )


    ws.append(
        [
            "Update Actions",
            audit.get("update_actions", 0)
        ]
    )


    ws.append(
        [
            "Delete Actions",
            audit.get("delete_actions", 0)
        ]
    )


    # Auto column width

    for column in ws.columns:

        max_length = 0

        column_letter = column[0].column_letter


        for cell in column:

            if cell.value:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )


        ws.column_dimensions[column_letter].width = max_length + 5


    # Risk Analysis Sheet

    risk_ws = wb.create_sheet(
    "Risk Analysis"
)


    risk_ws.append(
    [
        "Risk",
        "Severity",
        "Score",
        "Treatment Status"
    ]
)


    for risk in report["risk_list"]:

        risk_ws.append(
        [
            risk["title"],
            risk["severity"],
            risk["score"],
            risk["treatment_status"]
        ]
    )


# Audit Summary Sheet

    audit_ws = wb.create_sheet(
     "Audit Summary"
)


    audit_ws.append(
    [
        "Activity",
        "Count"
    ]
)


    audit_ws.append(
    [
        "Total Actions",
        report["audit_summary"]["total_actions"]
    ]
)


    audit_ws.append(
    [
        "Create Actions",
        report["audit_summary"]["create_actions"]
    ]
)


    audit_ws.append(
    [
        "Update Actions",
        report["audit_summary"]["update_actions"]
    ]
)

    audit_ws.append(
    [
        "Delete Actions",
        report["audit_summary"]["delete_actions"]
    ]
)


    for row in dashboard_ws.iter_rows():

        for cell in row:
            cell.font = Font(
            bold=True
        )

    # =========================
# Dashboard Charts
# =========================


# Risk Severity Chart

    risk_chart = PieChart()

    risk_labels = Reference(
    dashboard_ws,
    min_col=1,
    min_row=8,
    max_row=11
)

    risk_values = Reference(
    dashboard_ws,
    min_col=2,
    min_row=8,
    max_row=11
)


    risk_chart.add_data(
    risk_values,
    titles_from_data=False
)

    risk_chart.set_categories(
    risk_labels
)

    risk_chart.title = "Risk Distribution"


    dashboard_ws.add_chart(
    risk_chart,
    "D2"
)



# Control Compliance Chart

    control_chart = BarChart()


    control_labels = Reference(
    dashboard_ws,
    min_col=1,
    min_row=13,
    max_row=14
)


    control_values = Reference(
    dashboard_ws,
    min_col=2,
    min_row=13,
    max_row=14
)


    control_chart.add_data(
    control_values,
    titles_from_data=False
)


    control_chart.set_categories(
    control_labels
)


    control_chart.title = "Control Compliance"


    dashboard_ws.add_chart(
    control_chart,
    "D18"
)
    # =========================
# Format Audit Summary Sheet
# =========================

    for cell in audit_ws[1]:
      cell.font = Font(bold=True)
      cell.alignment = center


    for column in audit_ws.columns:

       max_length = 0

       column_letter = column[0].column_letter

    for cell in column:

        if cell.value:

            max_length = max(
                max_length,
                len(str(cell.value))
            )

    audit_ws.column_dimensions[column_letter].width = max_length + 5



# =========================
# Format Risk Analysis Sheet
# =========================

    # =========================
# Format Risk Analysis Sheet
# =========================

# =========================
# Format Risk Analysis Sheet
# =========================

    for cell in risk_ws[1]:
       cell.font = Font(bold=True)
       cell.alignment = center


    for row in risk_ws.iter_rows(
       min_row=2,
       min_col=2,
       max_col=2
):

        for cell in row:

            if cell.value == "Critical":

              cell.fill = PatternFill(
                "solid",
                fgColor="FF0000"
            )

            elif cell.value == "High":

                cell.fill = PatternFill(
                "solid",
                fgColor="FFA500"
            )

            elif cell.value == "Medium":

                cell.fill = PatternFill(
                "solid",
                fgColor="FFFF00"
            )


    for column in risk_ws.columns:

       max_length = 0

       column_letter = column[0].column_letter

       for cell in column:

          if cell.value:

            max_length = max(
                max_length,
                len(str(cell.value))
            )

    risk_ws.column_dimensions[column_letter].width = max_length + 5



    wb.save(file_name)


    return FileResponse(
    file_name,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    filename=file_name
)