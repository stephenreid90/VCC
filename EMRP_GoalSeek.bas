Attribute VB_Name = "EMRP_GoalSeek"
' ===========================================================================
'  Implied EMRP model — Goal Seek helper macros
'
'  SolveEMRP        : run from a button. Solves the implied return.
'  Worksheet_Change : OPTIONAL auto-solve. Do NOT keep this in the module
'                     below; instead copy it into the code module of the
'                     "Implied EMRP" sheet (right-click the sheet tab >
'                     View Code) so it fires when you edit an input.
'
'  How the solve works: Goal Seek drives cell C32 (PV - Price) to zero by
'  changing cell C29 (the discount rate). The implied EMRP then appears in
'  C35 (= implied return C34 - risk-free rate C11).
' ===========================================================================

Sub SolveEMRP()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Implied EMRP")
    ws.Range("C32").GoalSeek Goal:=0, ChangingCell:=ws.Range("C29")
    MsgBox "Implied EMRP = " & Format(ws.Range("C35").Value, "0.00%"), _
           vbInformation, "EMRP solved"
End Sub


' --- OPTIONAL: paste the block below into the "Implied EMRP" sheet module ---
'
' Private Sub Worksheet_Change(ByVal Target As Range)
'     Dim watch As Range
'     Set watch = Union(Me.Range("C6:C14"), Me.Range("C18:C27"))
'     If Not Intersect(Target, watch) Is Nothing Then
'         Application.EnableEvents = False
'         Me.Range("C32").GoalSeek Goal:=0, ChangingCell:=Me.Range("C29")
'         Application.EnableEvents = True
'     End If
' End Sub
