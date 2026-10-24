# Article submission content

Material for the article planned for this product. The product code on the default branch is unchanged.

| Item | Value |
|------|-------|
| Target venue | AiMH 2027 – 3rd International Conference on AI in Medicine and Healthcare |
| Type | conf |
| Deadline | 2027-02-28 – ثبت چکیده تا ۳۰ دسامبر ۲۰۲۶؛ ارسال تا ۲۸ فوریه ۲۰۲۷ |
| Official page | https://easychair.org/cfp/AIMH_2027 |
| Abstract rule (EasyChair conference) | Plain-text abstract pasted into the EasyChair form; avoid formatting, special symbols and references. Typical length 150–250 words; keywords 3–6. |

## Title
Stereochemistry-Aware Representations for Predicting Lipid-Nanoparticle Transfection: A Preliminary Study on Cis/Trans Lipids

## Abstract (draft)
The transfection efficiency of lipid nanoparticles depends on the molecular structure of the ionisable lipid, including its cis/trans stereochemistry, which many molecular representations ignore. This preliminary study tests whether a stereo-sensitive representation improves the prediction of transfection. We use the public LANTERN data: the AGILE set of about 1,100 lipids and the CisTrans set of 200 lipids. Compared with a representation that is blind to stereochemistry, the stereo-sensitive one reduced the RMSE from 2.24 to 1.83 and raised the Spearman correlation from 0.50 to 0.58. The result comes from a single random seed and the data contain no matched isomer pairs, so it cannot separate the effect of stereochemistry from other differences between lipids. At least ten seeds with confidence intervals, a graph-based model, matched isomer pairs from a new source and a comparison with the filed claims are [to be measured]. The study indicates that stereochemistry deserves explicit treatment in AI for gene-delivery design, in the context of AI in medicine and healthcare.

**Keywords:** lipid nanoparticles; stereochemistry; gene delivery; molecular representation; AI in medicine

## Before submitting
1. Replace every `[bracketed]` placeholder with values the team measured; nothing marked `[to be measured]` has a result yet.
2. Patent rule: do not disclose methods covered by this product's filed claims; a patent attorney must review before submission.
3. Add author names and affiliations; confirm the abstract limits in the venue's author guidelines (the limits above are typical for the venue family).
4. Numbers are the results recorded for this venue in the page database (owner's own runs). Check them against the paper-drafts before use; anything marked [to be measured] has not been measured. Only part of the claims was compared (claim 3426).
5. The Word file for the submission system is in the platform repository (`outputs/abstracts/`).
