# 🔍 Word Scanner for DOCX and PDF

This application scans Word (`.docx`) and PDF documents for trigger or banned words compiled from various published sources.

## 📚 Banned Word Sources
- [Thoughtcrime Checker](https://thoughtcrime-checker.com/banned-words.html)  
- [PEN America Banned Words List](https://pen.org/banned-words-list/)  
- [Grant Writing & Funding: Banned and Trigger Words](https://grantwritingandfunding.com/banned-and-trigger-words-in-federal-grant-writing-in-the-trump-administration-2-0/)  
- [U.S. Senate Report on NSF Banned Words](https://www.commerce.senate.gov/services/files/4BD2D522-2092-4246-91A5-58EEF99750BC)

## ⚙️ Features
- Upload DOCX or PDF files for scanning
- Use default banned word list and/or upload or enter your own
- View flagged words with context
- Export results as CSV to see all words in context or as Word with full document highlighting
- **No server-side storage** — all data is processed in-memory during your session

## 🔐 Data Security
- All uploads are encrypted in transit via HTTPS
- Files and generated results are stored in-memory only and discarded after session ends

## 🛠 Report Issues or Contribute
If you find additional word lists or notice a bug, please [submit an issue](https://github.com/childrens-bti/word-scanner/issues).

