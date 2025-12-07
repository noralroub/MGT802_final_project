# Quick Reference: Using the Editable Visual Abstract UI

## 🎯 What Changed?

The **Visual Abstract** tab (Tab 3) now has an editable form alongside a live preview. You can modify any field and see changes instantly.

---

## 📋 How to Use

### Step 1: Upload & Extract (Tab 1)
1. Upload a PDF file
2. Click "Extract & Analyze Paper"
3. Wait for processing to complete

### Step 2: Navigate to Visual Abstract (Tab 3)
1. Click the "Visual Abstract" tab
2. You'll see the editable form on the left and preview on the right

### Step 3: Edit Fields (Optional)
Edit any fields that need correction:

| Section | Fields | Example |
|---------|--------|---------|
| **Trial Info** | Title, Drug, Trial Name, Indication, Publication | Change "NEJM 2023" to "NEJM 2024" |
| **Population** | Total Enrolled, Arm Sizes, Mean Age | Update total from 17604 to 17605 |
| **Primary Outcome** | Label, Effect, Estimate, CI, P-value | Add confidence interval details |
| **Results & Safety** | Event Rates, Adverse Events, Dosing, Conclusions | Remove hallucinated adverse events |

### Step 4: View Preview
The preview updates **automatically** as you type. No need to click "Render" button!

### Step 5: Compare Original vs Edited (Optional)
Click "Compare Original vs Edited" to see what changed.

### Step 6: Save & Export (Optional)
Choose one of three options:

#### Option A: Copy to Clipboard
- Click "Copy to Clipboard"
- JSON data appears on screen
- Copy and paste elsewhere

#### Option B: Download as JSON
- Click "Download as JSON"
- File saves as `abstract_data.json`
- Import or use in other tools

#### Option C: Reset to Original
- Click "Reset to Original"
- All edits are discarded
- Returns to auto-extracted data

---

## 🔧 Editing Guide

### Text Fields (Title, Drug, Indication, etc.)
```
Click in the field → Type your text → Preview updates automatically
```

### Number Fields (Total Enrolled, Age, etc.)
```
Click in the field → Use up/down arrows or type → Must be a number
```

### Sliders (Event Rates)
```
Drag slider from 0-100% → Or click field and type percentage → Preview updates
```

### Text Areas (Adverse Events, Conclusions)
```
Click in the field → Type multiple lines → One item per line → Preview updates
```

### Buttons
```
Trial Info | Population | Outcomes | Results & Safety
↑ Click tab to switch between sections
```

---

## 📝 Common Editing Tasks

### Remove Hallucinated Adverse Events
1. Click "Results & Safety" tab
2. Find "Notable Adverse Events" text area
3. Delete lines that don't appear in the paper
4. Preview updates immediately

### Update Study Statistics
1. Click "Population" tab
2. Change "Total Enrolled" to correct number
3. Update "Arm 1 Size" and "Arm 2 Size"
4. Preview updates with new numbers

### Fix Missing Effect Size
1. Click "Outcomes" tab
2. Fill in "Estimate" field (e.g., "0.73")
3. Fill in "Confidence Interval" (e.g., "(0.66-0.82)")
4. Fill in "P-value" (e.g., "<0.001")
5. Preview shows complete results

### Modify Conclusions
1. Click "Results & Safety" tab
2. Find "Key Conclusions" text area
3. Edit or remove incorrect conclusions
4. Add correct conclusions
5. Preview updates immediately

---

## 💾 Saving Your Work

### To Keep Edited Data:
1. Click "Download as JSON" → Save file
2. Or click "Copy to Clipboard" → Paste elsewhere
3. Original auto-extracted data is always preserved

### To Start Over:
1. Click "Reset to Original"
2. All edits are cleared
3. Returns to auto-extracted version

---

## ✅ Best Practices

### DO:
- ✅ Use the preview to verify changes look correct
- ✅ Compare original vs edited before saving
- ✅ Download JSON as backup before making major changes
- ✅ Validate numbers against the paper before finalizing

### DON'T:
- ❌ Don't expect ALL auto-extracted data to be correct (yet)
- ❌ Don't forget to compare original vs edited
- ❌ Don't lose your edited data—always download/copy before leaving

---

## 🐛 Troubleshooting

### Preview Not Updating?
- Try clicking on a different field
- Refresh the page if stuck
- Changes should update within 1-2 seconds

### Numbers Show as "Invalid"?
- Make sure you're entering only numbers (0-9, decimals OK)
- No text or special characters in number fields
- Event rates must be 0-100

### JSON Download Not Working?
- Try "Copy to Clipboard" instead
- Make sure pop-ups are not blocked
- Try different browser if issues persist

### Want to Edit Multiple Outcomes?
- **Phase 2 coming soon!** Will support N outcomes
- For now, use the single primary outcome field
- Add additional outcomes in conclusions if needed

---

## 🚀 What's Coming Next?

### Phase 2 (Coming Soon):
- Support for **multiple outcomes** (primary + secondary)
- Support for **different trial types** (not just cardiovascular)
- **Better extraction** (fewer hallucinations)

### Phase 3 (Coming Soon):
- **Adaptive template** (adjusts to data complexity)
- Different layouts for simple vs complex trials

### Phase 4 (Coming Soon):
- **Citation tracking** (see where data came from)
- **Confidence scores** (know which fields might be wrong)
- **Hallucination detection** (automatically flag suspicious data)

---

## 📞 Questions?

### "Can I edit outcomes?"
Yes! Click "Outcomes" tab and edit all fields.

### "Will my edits be saved?"
Only if you download as JSON. Otherwise, they're lost when you leave the page.

### "Can I add more outcomes?"
Phase 1 supports 1 primary outcome. Phase 2 will support multiple outcomes.

### "What if I make a mistake?"
Click "Reset to Original" to start fresh.

### "Can I export to other formats?"
Currently JSON only. Phase 3+ will add PDF, SVG, PowerPoint.

---

## 📊 Data Structure Reference

### What Gets Saved (JSON Format):
```json
{
  "trial_info": {
    "title": "...",
    "drug": "...",
    "indication": "...",
    "trial_name": "...",
    "publication": "..."
  },
  "population": {
    "total_enrolled": 0,
    "arm_1_label": "...",
    "arm_1_size": 0,
    "arm_2_label": "...",
    "arm_2_size": 0,
    "age_mean": 0.0
  },
  "primary_outcome": {
    "label": "...",
    "effect_measure": "...",
    "estimate": "...",
    "ci": "...",
    "p_value": "..."
  },
  "event_rates": {
    "arm_1_percent": 0.0,
    "arm_2_percent": 0.0
  },
  "adverse_events": {
    "summary": "...",
    "notable": ["...", "..."]
  },
  "dosing": {
    "description": "..."
  },
  "conclusions": ["...", "..."]
}
```

---

## 🎓 Example Workflow

### Scenario: You Found an Error in Auto-Extraction

**Step 1: Identify the Error**
- Auto-extract says "Semaglutide" as drug
- Paper actually tested "Tirzepatide"

**Step 2: Navigate to Edit Form**
- Click "Trial Info" tab

**Step 3: Make the Correction**
- Change "Drug/Intervention" from "Semaglutide" to "Tirzepatide"

**Step 4: Verify in Preview**
- Right column shows updated abstract with "Tirzepatide"

**Step 5: Save the Correction**
- Click "Download as JSON"
- File saves with corrected data

**Step 6: Use Corrected Data**
- Re-import JSON in future sessions
- Use in other tools

---

## 📈 User Feedback Template

If you find issues, use this template:

```
**Field**: [Which field has the problem?]
**Expected**: [What should be there?]
**Actual**: [What's currently there?]
**Source**: [Where in the paper does it say this?]
**Impact**: [Does it break the visual abstract?]
```

Example:
```
**Field**: Primary Outcome > Estimate
**Expected**: 0.73
**Actual**: 0.80
**Source**: Page 5, Results section, first paragraph
**Impact**: Yes, makes results look better than they are
```

---

## ✨ Summary

You now have complete control over the visual abstract:

- ✅ Edit any field
- ✅ See changes instantly
- ✅ Compare original vs edited
- ✅ Export corrected data
- ✅ Reset if needed

**Use these tools to validate extraction against your paper and correct any errors!**

