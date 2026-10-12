# Predeclared checks

The first returned workbook is the scored candidate. Do not repair it before checking.

- Formula integrity passes only if every baseline formula remains in the same sheet and cell with identical text, and no unexpected formula is added.
- Task completion requires B3 to be 4 and E1:E4 to match the requested status header and values.
- Content integrity requires all other populated cells and sheet names/order to remain unchanged. Changes in blank-cell formatting are not measured automatically.
- Recalculation is a human check: open the workbook in a spreadsheet application, recalculate and compare totals with arithmetic from the edited inputs. Record the application and version.
- Formatting is a human check: compare headers, column widths, freeze panes and number display with the baseline.

Record pass or fail and evidence for each human check, plus actual task and correction time. The automated `passed` field covers only the automatic checks; it is not an overall verdict. Keep the baseline, original candidate, checked result and any corrected copy separately.
