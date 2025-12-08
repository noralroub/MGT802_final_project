# Phase 2 Testing Guide - Quick Start

## System Status
✅ Phase 2 agents: implemented and tested (12/12 tests passing)
✅ Integration: complete, app.py updated
✅ Ready for: cardiovascular trial PDF testing

---

## How to Test Locally

### Step 1: Start the Streamlit App
```bash
cd /Users/Noralroub/Downloads/MGT802_final_project
python3 -m streamlit run app.py
```

Opens at: `http://localhost:8501`

### Step 2: Upload a PDF
1. Go to **📄 Upload & Extract** tab
2. Click "Choose a PDF file"
3. Select a cardiovascular clinical trial paper (PDF format)
4. Verify file loads: shows filename and file size

### Step 3: Extract & Analyze
1. Click **"🔄 Extract & Analyze Paper"** button
2. Watch extraction progress (spinner shows processing)
3. See extraction summary:
   - **Title:** Paper title (first 50 chars)
   - **Population:** Extracted population size
   - **Validation Issues:** Number of issues detected

### Step 4: Review Visual Abstract
1. Go to **🎨 Visual Abstract** tab
2. See auto-populated fields:
   - Main finding (from results)
   - Background and methods
   - Population size and intervention
   - Key results
3. Review **validation issues** (if any):
   - Shows specific issues detected by fact-checker
   - Helps identify extraction accuracy

### Step 5: Edit & Customize
1. Use sidebar editor to customize fields
2. Live preview updates as you edit
3. Fields available to edit:
   - Title
   - Main finding
   - Background
   - Methods
   - Participants
   - Intervention vs. Comparator
   - Results
   - Journal/authors/DOI

### Step 6: Verify Against Publisher Abstract
1. Open original paper's publisher abstract
2. Compare extraction results:
   - ✅ Population size matches?
   - ✅ Main finding accurate?
   - ✅ Intervention/comparator correct?
   - ✅ Key results captured?
   - ✅ Any hallucinations?

---

## What Gets Extracted

### Metadata
- Title
- Authors (list)
- Journal
- Year
- DOI
- Study type (RCT, observational, cohort, etc.)

### Background
- Background text (2-4 sentences)
- Research question

### Design
- Population size (integer)
- Intervention description
- Comparator description
- Primary outcomes (list)

### Results
- Main finding (with statistics if available)
- Key results (3-5 items)
- Adverse events summary

### Limitations
- List of 3-5 study limitations

### Data Quality
- Validation issues (if any)
  - Population size must be > 0
  - Hazard ratios must be 0.01-10
  - P-values must be 0-1
  - Percentages must be 0-100
  - Ages must be 0-120

---

## Expected Behavior

### Successful Extraction
```
✅ PDF processed and analyzed successfully!
📊 Metrics shown
🎨 Visual Abstract auto-populated
```

### Issues Found
```
⚠️ N validation issue(s) found during extraction:
  • Issue 1
  • Issue 2
  (Can still view and edit in Visual Abstract tab)
```

### Error Handling
```
❌ Error processing PDF: [detailed error]
(Check logs for troubleshooting)
```

---

## Testing on Different Paper Types

### Best Case (Well-Formatted Trial)
- Expected: All fields populated, 0 validation issues
- Time: ~30-60 seconds

### Complex Trial (Multiple Arms/Subgroups)
- Expected: Main results extracted, some ambiguity
- Time: ~30-60 seconds
- Action: Edit to clarify which arm is comparator

### Short Paper (Limited Methods)
- Expected: Some fields empty, but basics captured
- Time: ~30 seconds
- Action: Edit sidebar to fill missing context

### Real-World Paper (Mixed Format)
- Expected: 80-90% of data captured, 1-3 validation issues
- Time: ~30-60 seconds
- Action: Review and correct any hallucinations

---

## Quick Test Checklist

For each PDF, verify:

- [ ] PDF uploads successfully
- [ ] "Extract & Analyze" completes without error
- [ ] Extraction metrics display correctly
- [ ] Visual abstract tab shows extracted data
- [ ] Population size is a reasonable number
- [ ] Main finding contains trial results
- [ ] Background describes the clinical need
- [ ] Intervention/comparator are clearly stated
- [ ] Validation issues (if any) are relevant
- [ ] User can edit each field in sidebar
- [ ] Live preview updates while editing

---

## Troubleshooting

### PDF Won't Upload
- Check file is valid PDF
- Try smaller file (< 50 MB)
- Check browser console (F12) for errors

### Extraction Times Out
- Large PDFs take longer (normal)
- Check API key is valid (config.py)
- Check internet connection to OpenAI

### Extraction Returns Empty Results
- PDF might not be a clinical trial
- Try a different paper
- Check logs for specific extraction errors

### Visual Abstract Won't Display
- Refresh the page
- Check browser console (F12)
- Verify PDF was extracted successfully

### Missing Fields in Visual Abstract
- Normal for some papers (background, DOI, etc.)
- Edit sidebar to manually add
- System still generates valid abstract

---

## Testing Schedule

### Phase 1: Single Paper (30 min)
- Pick 1 well-formatted trial
- Test full workflow
- Verify no errors

### Phase 2: Diverse Papers (2-3 hours)
- Test 5 different cardiovascular trials
- Vary by:
  - Study type (RCT, observational, cohort)
  - Intervention type (drug, device, behavioral)
  - Publication date (recent vs. historical)
  - Journal format (structured abstract vs. narrative)

### Phase 3: Comparison & Refinement (1-2 hours)
- Compare extracted data to publisher abstracts
- Track accuracy for each field
- Note patterns in errors/hallucinations
- Refine agent prompts if needed

---

## Performance Expectations

### Speed
- **Small PDF (10-20 pages):** 30-45 seconds
- **Medium PDF (20-40 pages):** 45-60 seconds
- **Large PDF (40+ pages):** 60-90 seconds
- (Includes: PDF ingestion, 10 parallel summaries, 5 parallel extractions, fact-checking)

### Accuracy
- **Best case:** 95-100% (well-formatted trials)
- **Typical case:** 80-90% (real-world papers)
- **Worst case:** 50-70% (unusual formats, hallucinations)
- (Measured against publisher abstracts)

### Resource Usage
- **CPU:** 4-6 threads active during extraction
- **Memory:** ~200-300 MB during processing
- **API calls:** ~20 LLM calls per PDF (10 summaries + 5 extractions + 1 combiner)

---

## Data Privacy Note

- PDFs are ingested locally
- Text is sent to OpenAI API for extraction
- No data is stored permanently
- All session data cleared when browser closes

---

## Common Questions

**Q: Why does it take 30+ seconds?**
A: 10 parallel summary agents + 5 parallel extraction agents make multiple LLM calls. This is expected.

**Q: Can I use this on proprietary papers?**
A: Yes, but be aware text goes to OpenAI API. Check your institution's policies.

**Q: What if extraction is 100% wrong?**
A: Use sidebar to manually edit all fields. The visual abstract is still generated correctly.

**Q: Can I export the result?**
A: HTML preview shown in app. PNG export requires additional setup (see PHASE_1_COMPLETION.md).

**Q: How do I improve extraction accuracy?**
A: Agent prompts can be refined based on testing results. See agent files for prompt tuning.

---

## Next Steps After Testing

1. **Collect Results**
   - Record accuracy metrics for each paper
   - Note common error patterns
   - Track validation issues

2. **Refine Agents**
   - Update prompts based on errors
   - Adjust extraction logic if needed
   - Retrain on edge cases

3. **Expand Testing**
   - Test on additional paper types
   - Test on different intervention types
   - Test on different trial designs

4. **Consider Upgrades**
   - Add CrewAI for agent collaboration (future)
   - Implement semantic validation (future)
   - Add multi-model extraction (future)

---

## Support

For issues or questions:
1. Check Phase2_INTEGRATION.md for architecture details
2. Review agent files (agents/*.py) for extraction logic
3. Check test_phase2_agents.py for validation examples
4. Inspect logs in terminal for detailed error info

---

**Ready to test! Start with Step 1 above and upload your first cardiovascular trial PDF.**
