# Open-source AL / API references for creating and posting General Journal lines in Business Central (opening balances)

Scope note: all BCApps citations below were verified against the `main` branch of `microsoft/BCApps` at commit `9f954e85cbed82e2c18b77d8513c22a7d2b2e035` (APIV2 app.json reports `"version": "30.0.0.0"`, i.e. the in-development 2027-wave-1 codebase). BCApps also carries release branches `releases/24.x` … `releases/29.x` (verified via `git ls-remote`), so the same paths can be pinned to v24–v28 by swapping the commit for a branch name. Object IDs/names quoted here are the ones in the files at that commit. Microsoft Learn (`learn.microsoft.com`), `yzhums.com` and `demiliani.com` were **not reachable** through this session's egress proxy, so those sources are cited only through search-result snippets and marked as such.

Permalink conventions used below:
- Blob: `https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/<path>`
- Raw: `https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/<path>`

---

## 1. Microsoft's API v2.0 journal pages ("APIV2 - Journals", "APIV2 - JournalLines", "APIV2 - Customer Payments") and the codeunits behind them

### Takeaway
The v2.0 journal API lives in the separate `_Exclude_APIV2_` app (`src/Apps/W1/APIV2`), not in the base app; the pages are **page 30016 "APIV2 - Journals"** (not 30002), **page 30049 "APIV2 - JournalLines"** and **page 30055 "APIV2 - Customer Payments"**. The `post` action simply calls `Codeunit.RUN(Codeunit::"Gen. Jnl.-Post", GenJournalLine)` on the batch; line field mapping is done by base-app codeunit **5478 "Graph Mgt - Journal Lines"** (`SetJournalLineValues`) and **5469 "Library API - General Journal"** (`InitializeLine`). The journalLines page hard-filters to `Document Type = " "` and `Account Type` in `G/L Account..Bank Account` (enum values 0..3, so Customer and Vendor are technically inside the range but the page only resolves `accountId` for G/L and Bank accounts), and it does **not** expose Document Type, Due Date, Currency Code or Applies-to fields.

### Cited Findings

**Object identities and locations (BCApps `main`, commit 9f954e8):**
- `page 30016 "APIV2 - Journals"` — `APIVersion = 'v2.0'`, `EntityName = 'journal'`, `EntitySetName = 'journals'`, `SourceTable = "Gen. Journal Batch"`, `ODataKeyFields = SystemId`, `Extensible = false`; sub-part `journalLines` bound to `"APIV2 - JournalLines"` with `SubPageLink = "Journal Batch Id" = field(SystemId)` — [APIV2Journals.Page.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2Journals.Page.al) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2Journals.Page.al)
- `page 30049 "APIV2 - JournalLines"` — `EntityName = 'journalLine'`, `EntitySetName = 'journalLines'`, `SourceTable = "Gen. Journal Line"`, `DelayedInsert = true`, `Extensible = false` — [APIV2JournalLines.Page.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2JournalLines.Page.al) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2JournalLines.Page.al)
- `page 30055 "APIV2 - Customer Payments"` — `EntityName = 'customerPayment'`, `EntitySetName = 'customerPayments'`, `SourceTable = "Gen. Journal Line"` — [APIV2CustomerPayments.Page.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2CustomerPayments.Page.al)
- Sibling pages in the same folder: `APIV2CustPaymJournals.Page.al`, `APIV2VendorPaymJournals.Page.al`, `APIV2DimensionSetLines.Page.al` — [folder listing from git tree](https://github.com/microsoft/BCApps/tree/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages)
- The APIV2 app manifest: `"id": "10cb69d9-bc8a-4d27-970a-9e110e9db2a5"`, `"name": "_Exclude_APIV2_"`, `"version": "30.0.0.0"` — [app.json](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/app.json)
- Base-app helper codeunits: `codeunit 5478 "Graph Mgt - Journal Lines"`, `codeunit 5482 "Graph Mgt - Journal"`, `codeunit 5479 "Graph Mgt - Customer Payments"` under `src/Layers/W1/BaseApp/Integration/Graph/`; `codeunit 5469 "Library API - General Journal"` under `src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/` — [GraphMgtJournalLines.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtJournalLines.Codeunit.al), [GraphMgtJournal.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtJournal.Codeunit.al), [GraphMgtCustomerPayments.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtCustomerPayments.Codeunit.al), [LibraryAPIGeneralJournal.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/LibraryAPIGeneralJournal.Codeunit.al)
- No codeunit literally named "Journal API" exists in the BCApps tree; the name search over the full `git ls-tree` only matched the three `GraphMgt*` codeunits above — [tree search, this session; source tree root](https://github.com/microsoft/BCApps/tree/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph)

**The `post` action (APIV2 - Journals):**
```al
[ServiceEnabled]
[Caption('Posts all journal lines in the batch to the general ledger')]
[Scope('Cloud')]
procedure post(var ActionContext: WebServiceActionContext)
var
    GenJournalBatch: Record "Gen. Journal Batch";
begin
    GetBatch(GenJournalBatch);
    PostBatch(GenJournalBatch);
    SetActionResponse(ActionContext, Rec.SystemId);
end;

local procedure PostBatch(var GenJournalBatch: Record "Gen. Journal Batch")
var
    GenJournalLine: Record "Gen. Journal Line";
begin
    GenJournalLine.SetRange("Journal Template Name", GenJournalBatch."Journal Template Name");
    GenJournalLine.SetRange("Journal Batch Name", GenJournalBatch.Name);
    if not GenJournalLine.FindFirst() then
        Error(ThereIsNothingToPostErr);

    Codeunit.RUN(Codeunit::"Gen. Jnl.-Post", GenJournalLine);
end;
```
— [APIV2Journals.Page.al L100-L122](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2Journals.Page.al#L100-L122). The action response is `WebServiceActionResultCode::Deleted` (HTTP 204) — same file L130-L136.
- Journal (batch) fields exposed: `id` (SystemId), `code` (Name, ShowMandatory), `displayName` (Description), `templateDisplayName` ("Journal Template Name"), `lastModifiedDateTime` (SystemModifiedAt), `balancingAccountId` (BalAccountId), `balancingAccountNumber` ("Bal. Account No.", Editable=false) — same file L28-L58.
- `OnNewRecord` defaults `"Journal Template Name" := GraphMgtJournal.GetDefaultJournalLinesTemplateName()`; `OnFindRecord` filters to that default template unless a template filter or `SystemId` filter is supplied — same file L74-L93.
- `GetDefaultJournalLinesTemplateName()` = first `Gen. Journal Template` with `"Page ID" = PAGE::"General Journal"`, `Recurring = false`, `Type = 0` (General). Customer payments use `PAGE::"Cash Receipt Journal"`/`Type = 3`; vendor payments use `PAGE::"Payment Journal"`/`Type = 4` — [GraphMgtJournal.Codeunit.al L16-L50](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtJournal.Codeunit.al#L16-L50)

**Fields exposed by `APIV2 - JournalLines` and their table 81 mapping** (all from [APIV2JournalLines.Page.al L30-L183](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2JournalLines.Page.al#L30-L183)):

| API property | Gen. Journal Line field (field no.) | Notes |
|---|---|---|
| `id` | `SystemId` | Editable=false |
| `journalId` | `"Journal Batch Id"` (8006) | required via filter or body (`CheckFilters`) |
| `journalDisplayName` | `"Journal Batch Name"` (51) via page var `GlobalJournalDisplayNameTxt` | read-only; OnValidate raises `CannotEditBatchNameErr` |
| `lineNumber` | `"Line No."` (2) | |
| `accountType` | `"Account Type"` (3, Enum "Gen. Journal Account Type") | |
| `accountId` | `"Account Id"` (8001) | OnValidate resolves G/L Account or Bank Account by SystemId only |
| `accountNumber` | `"Account No."` (4) | OnValidate back-fills `"Account Id"` for G/L and Bank only |
| `postingDate` | `"Posting Date"` (5) | |
| `documentNumber` | `"Document No."` (7) | |
| `externalDocumentNumber` | `"External Document No."` (77) | |
| `amount` | `Amount` (13) | |
| `description` | `Description` | |
| `comment` | `Comment` | |
| `taxCode` | page var → `"VAT Prod. Posting Group"` (91) if `GeneralLedgerSetup.UseVat()` else `"Tax Group Code"` (84) | |
| `balanceAccountType` | `"Bal. Account Type"` (63) | |
| `balancingAccountId` | `"Balance Account Id"` (8008) | resolves G/L or Bank by SystemId |
| `balancingAccountNumber` | `"Bal. Account No."` (11) | |
| `lastModifiedDateTime` | `SystemModifiedAt` | Editable=false |
| `attachments` (part) | `"APIV2 - Attachments"`, `"Document Type" = const(Journal)` | |
| `dimensionSetLines` (part) | `"APIV2 - Dimension Set Lines"`, `"Parent Type" = const("Journal Line")` | |

Field numbers come from [GenJournalLine.Table.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalLine.Table.al) (`table 81 "Gen. Journal Line"`; e.g. `field(8001; "Account Id"; Guid)`, `field(8006; "Journal Batch Id"; Guid)`, `field(8008; "Balance Account Id"; Guid)`, `field(8002; "Customer Id"; Guid)`, `field(8009; "Vendor Id"; Guid)`, `field(8003; "Applies-to Invoice Id"; Guid)`, `field(480; "Dimension Set ID"; Integer)`).

**Account types allowed by the journalLines API:**
```al
trigger OnNewRecord(BelowxRec: Boolean)
begin
    ClearCalculatedFields();
    Rec."Document Type" := Rec."Document Type"::" ";
    Rec."Account Type" := Rec."Account Type"::"G/L Account";
end;

trigger OnOpenPage()
begin
    Rec.SetRange("Document Type", Rec."Document Type"::" ");
    Rec.SetRange("Account Type", Rec."Account Type"::"G/L Account", Rec."Account Type"::"Bank Account");
end;
```
— [APIV2JournalLines.Page.al L253-L265](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2JournalLines.Page.al#L253-L265)
- `enum 81 "Gen. Journal Account Type"` values: 0 "G/L Account", 1 Customer, 2 Vendor, 3 "Bank Account", 4 "Fixed Asset", 5 "IC Partner", 6 Employee, 10 "Allocation Account" — [GenJournalAccountType.Enum.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalAccountType.Enum.al). Therefore the page's `SetRange("G/L Account", "Bank Account")` is the numeric range 0..3, which includes Customer (1) and Vendor (2) on read, but `accountId`/`accountNumber` validation only handles G/L and Bank accounts.
- `enum 6 "Gen. Journal Document Type"`: 0 " ", 1 Payment, 2 Invoice, 3 "Credit Memo", 4 "Finance Charge Memo", 5 Reminder, 6 Refund — [GenJournalDocumentType.Enum.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalDocumentType.Enum.al)
- In the older `SetJournalLineFilters` (used by v1.0/beta) the account filter was `G/L Account` only; `SetJournalLineFiltersV1` widened it to `"G/L Account".."Bank Account"` — [GraphMgtJournalLines.Codeunit.al L38-L50](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtJournalLines.Codeunit.al#L38-L50)

**Insert pipeline (what a POST to journalLines actually does):**
```al
trigger OnInsertRecord(BelowxRec: Boolean): Boolean
var
    GenJournalBatch: Record "Gen. Journal Batch";
    TempGenJournalLine: Record "Gen. Journal Line" temporary;
begin
    if IsNullGuid(Rec."Journal Batch Id") then
        CheckFilters();
    TempGenJournalLine.Reset();
    TempGenJournalLine.Copy(Rec);
    Clear(Rec);
    if IsNullGuid(TempGenJournalLine."Journal Batch Id") then
        GenJournalBatch.GetBySystemId(TempGenJournalLine.GetFilter("Journal Batch Id"))
    else
        GenJournalBatch.GetBySystemId(TempGenJournalLine."Journal Batch Id");
    GraphMgtJournalLines.SetJournalLineTemplateAndBatchV2(Rec, GenJournalBatch);
    LibraryAPIGeneralJournal.InitializeLine(
      Rec, TempGenJournalLine."Line No.", TempGenJournalLine."Document No.", TempGenJournalLine."External Document No.");
    GraphMgtJournalLines.SetJournalLineValues(Rec, TempGenJournalLine);
    SetCalculatedFields();
end;
```
— [APIV2JournalLines.Page.al L205-L229](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2JournalLines.Page.al#L205-L229). `CheckFilters` raises `'You must specify a journal batch ID or a journal ID to get a journal line.'` when neither a `Journal Batch Id` filter nor a `SystemId` filter is present (L301-L307).
- `SetJournalLineValues` validation order: `Validate("Account Type")` → `Validate("Account No.")` → `Validate("Posting Date")` (if non-zero) → `Validate("Document Type", " ")` → `Validate("Document No.")` (if non-blank) → `Validate("External Document No.")` → `Validate(Amount)` → `Validate(Description)` → `Validate(Comment)` → `Validate("Bal. Account No.", '')` → copy `"Bal. Account Type"`/`"Bal. Account No."` from the batch → override with the request's balance account if different → `Validate("Tax Group Code")` → if `CopyVATSetupToJnlLines()` then copy Gen./VAT posting groups raw (no Validate) — [GraphMgtJournalLines.Codeunit.al L52-L84, L116-L128](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtJournalLines.Codeunit.al#L52-L84)
- `SetJournalLineTemplateAndBatchV2` does `Validate("Journal Template Name", GenJournalBatch."Journal Template Name")` then `Validate("Journal Batch Name", GenJournalBatch.Name)` and sets matching `SetRange`s — same file L29-L36.
- `InitializeLine` (codeunit 5469): gets the batch, sets `"Line No."`, replicates page behaviour by copying values from the previous/next line (`SetUpNewLine`), assigns `"External Document No."`, and if `DocumentNo = ''` derives a document number via `AlterDocNoBasedOnExternalDocNo` — [LibraryAPIGeneralJournal.Codeunit.al L37-L65](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/LibraryAPIGeneralJournal.Codeunit.al#L37-L65). `EnsureGenJnlBatchExists` creates a batch with `GenJournalBatch.SetupNewBatch()` and `Insert(true)` + `Commit()` (L71-L83).
- `OnModifyRecord` disallows changing `"Journal Batch Id"` (`CannotEditBatchIdErr`) and uses `Rename` when `"Line No."` changes — page L231-L251.

**Customer Payments API (document-type Payment pattern):**
- `OnNewRecord` sets `"Document Type" := Payment` and `"Account Type" := Customer`; `OnInsertRecord` uses `GraphMgtCustomerPayments.SetCustomerPaymentsTemplateAndBatch(Rec, LibraryAPIGeneralJournal.GetBatchNameFromId(JournalBatchId))`, `InitializeLine(...)`, then `SetCustomerPaymentsValues` — [APIV2CustomerPayments.Page.al L212-L276](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/app/src/pages/APIV2CustomerPayments.Page.al#L212-L276)
- Exposed fields: `id, journalId, journalDisplayName, lineNumber, customerId, customerNumber, postingDate, documentNumber, externalDocumentNumber, amount, appliesToInvoiceId, appliesToInvoiceNumber, description, comment, lastModifiedDateTime, dimensionSetLines` — same file L30-L189.
- `SetPaymentsValues` (codeunit 5478) hard-codes `Validate("Document Type", Payment)` and `Validate("Applies-to Doc. Type", Invoice)`, assigns `"Applies-to Doc. No."` without Validate, validates `"Applies-to Invoice Id"` when set, and copies the batch balancing account — [GraphMgtJournalLines.Codeunit.al L86-L114](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtJournalLines.Codeunit.al#L86-L114)
- `SetCustomerPaymentsFilters`: `Document Type = Payment`, `Account Type = Customer`, `Applies-to Doc. Type = Invoice`, default Cash Receipt template — [GraphMgtCustomerPayments.Codeunit.al L29-L35](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Integration/Graph/GraphMgtCustomerPayments.Codeunit.al#L29-L35)

**Microsoft Learn (search snippets only; site unreachable from this session):**
- "The journal resource type offers a bound action called post which posts the corresponding journal batch… `POST .../companies({id})/journals({id})/Microsoft.NAV.post`" with a 204 response — [learn.microsoft.com dynamics_journal (v2.0)](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/resources/dynamics_journal) (snippet via WebSearch)
- Line creation: "POST businesscentralPrefix/companies({id})/journals({id})/journalLines … returns 201 Created and the journalLines object" — [learn.microsoft.com dynamics_journalline_create](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/api/dynamics_journalline_create) (snippet via WebSearch)
- Power Automate users hit "You must specify a journal batch ID or a journal ID" when posting to `journalLines` without the parent journal route; one thread attributes it to `CheckFilters` and another suggests "create a custom API in BC based on the original journallines API" — [powerusers.microsoft.com thread](https://powerusers.microsoft.com/t5/Building-Flows/Create-record-in-Business-Central-Journal-Lines/m-p/2217413) (snippet via WebSearch)

### Inferences
- The standard `journalLines` entity cannot carry `Document Type`, `Due Date`, `Currency Code`, `Applies-to Doc. No.`, `Gen. Posting Type` or posting groups, and resolves `accountId` only for G/L and Bank accounts. For opening balances of customers/vendors (Invoice/Credit Memo lines with due dates) you need either (a) a custom API page over table 81 (pattern: copy page 30049, drop the `OnOpenPage` filters, add the extra fields and validate them in `OnInsertRecord` in the same order as `SetJournalLineValues`), or (b) write lines from AL and expose only a posting action.
- The `post` action posts **all** lines in the batch regardless of account type — the E2E test (section 6) proves this by creating two `Document Type::Invoice` / `Account Type::Customer` lines in AL and posting them via `journals({id})/Microsoft.NAV.post`. So mixed-type opening-balance batches created by a custom API can still be posted with the standard action.
- `SetJournalLineValues` calls `Validate("Bal. Account No.", '')` first, then re-applies the batch's balancing account — so the batch-level `balancingAccountId` is the intended way to set the suspense/opening-balance account, and a per-line `balancingAccountNumber` overrides it.
- Because `taxCode` maps to `VAT Prod. Posting Group` only when `UseVat()` is true and posting groups are copied **without** Validate, an opening-balance implementation should either leave `Gen. Posting Type` blank (so no VAT is calculated) or validate groups explicitly in custom code.

### Gaps
- Could not fetch the Microsoft Learn `journalLine` resource page itself (proxy denied `learn.microsoft.com`), so the official JSON property table was not captured verbatim; the field list above is from the AL source, which is authoritative.
- Did not locate any Microsoft codeunit named "Journal API"; if the requester saw that name elsewhere it may refer to older NAV 2018 "Graph" naming.

---

## 2. How the standard app posts a journal batch in AL (codeunits 231 / 13 / 12 / 11) and the Gen. Journal Line validation order

### Takeaway
The correct numbering is **codeunit 231 "Gen. Jnl.-Post"** (UI wrapper: confirmations, job-queue, calls batch), **codeunit 13 "Gen. Jnl.-Post Batch"** (locks, checks every line via codeunit 11, balances per document/date, assigns document numbers from the batch's `Posting No. Series`, posts each line with `GenJnlPostLine.RunWithoutCheck`, deletes lines, commits), **codeunit 12 "Gen. Jnl.-Post Line"** (`RunWithCheck`/`RunWithoutCheck` → ledger entries), and **codeunit 11 "Gen. Jnl.-Check Line"** (`RunCheck`). Headless code should use `Codeunit.Run(Codeunit::"Gen. Jnl.-Post Batch", GenJnlLine)` (as Microsoft's GP migration does) or `GenJnlPostLine.RunWithCheck()` per line inside its own transaction.

### Cited Findings

**Codeunit identities (BCApps `main`, folder `src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/` and `/Journal/`):**
- `codeunit 231 "Gen. Jnl.-Post"`, `TableNo = "Gen. Journal Line"`, `EventSubscriberInstance = Manual` — [GenJnlPost.Codeunit.al L23-L26](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPost.Codeunit.al#L23-L26) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPost.Codeunit.al)
- `codeunit 13 "Gen. Jnl.-Post Batch"`, `TableNo = "Gen. Journal Line"` — [GenJnlPostBatch.Codeunit.al L37-L42](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L37-L42) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al)
- `codeunit 12 "Gen. Jnl.-Post Line"`, `TableNo = "Gen. Journal Line"`, 11,258 lines; public entry points `procedure RunWithCheck(var GenJnlLine2: Record "Gen. Journal Line"): Integer` (L209) and `procedure RunWithoutCheck(...)` (L235), both wrapping `local procedure "Code"(var GenJnlLine; CheckLine: Boolean)` (L252); per-account posting routines `PostGLAcc` (L1200), `PostCust` (L1255), `PostVend` (L1376), `PostEmployee` (L1497), `PostBankAcc` (L1574), `PostFixedAsset` (L1718); `StartPosting` (L1906), `FinishPosting` (L2047), `GetNextTransactionNo` (L7660) — [GenJnlPostLine.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostLine.Codeunit.al) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostLine.Codeunit.al)
- `codeunit 11 "Gen. Jnl.-Check Line"`, `TableNo = "Gen. Journal Line"`, `procedure RunCheck(var GenJnlLine)` at L115, `DateNotAllowed` L349/L376, `SetBatchMode` L1040, local `CheckDates` L519, `CheckAccountNo` L564, `CheckBalAccountNo` L668, `CheckDimensions` L937, `CheckZeroAmount` L969, `CheckAccountType` L1087, `CheckAppliesToDocNo` L1147 — [GenJnlCheckLine.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJnlCheckLine.Codeunit.al) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJnlCheckLine.Codeunit.al)
- `codeunit "Gen. Jnl.-Post via Job Queue"` also exists in the same Posting folder (`GenJnlPostviaJobQueue.Codeunit.al`) — [folder](https://github.com/microsoft/BCApps/tree/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting)

**Codeunit 231 flow ("Code"):** gets template; `GenJnlTemplate.TestField("Force Posting Report", false)`; recurring templates must not have a Posting Date filter; unless `PreviewMode or HideDialog`, asks `'Do you want to post the journal lines?'` via `ConfirmManagement.GetResponseOrDefault(Text001, true)`; `GenJnlPostBatch.ConfirmPostingUnvoidableChecks(...)`; if `GeneralLedgerSetup."Post with Job Queue"` and not preview, schedules via `Gen. Jnl.-Post via Job Queue`; otherwise runs `Gen. Jnl.-Post Batch`. `OnBeforeCode(GenJnlLine, HideDialog)` lets subscribers set `HideDialog := true` — [GenJnlPost.Codeunit.al L57-L125](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPost.Codeunit.al#L57-L125)

**Codeunit 13 flow:**
```al
local procedure "Code"(var GenJnlLine: Record "Gen. Journal Line")
...
    GenJnlLine.SetRange("Journal Template Name", GenJnlLine."Journal Template Name");
    GenJnlLine.SetRange("Journal Batch Name", GenJnlLine."Journal Batch Name");
    GenJnlLine.LockTable();
    GenJnlAlloc.LockTable();
    GenJnlTemplate.Get(GenJnlLine."Journal Template Name");
    GenJnlBatch.Get(GenJnlLine."Journal Template Name", GenJnlLine."Journal Batch Name");
    GLSetup.Get();
    ...
    ProcessLines(GenJnlLine);
```
— [GenJnlPostBatch.Codeunit.al L155-L188](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L155-L188)
- `ProcessLines`: if no lines found (`Find('=><')`), checks `DateNotAllowed` and commits; then `GenJnlCheckLine.SetBatchMode(true)` and loops `CheckLine(GenJnlLine, PostingAfterWorkingDateConfirmed)` for every line; `GLEntry.LockTable()`; `FindSet(true)` and posts; `UpdateAndDeleteLines`; `NoSeriesBatch.SaveState()`; `OnBeforeCommit`; `Commit()` unless `SuppressCommit`; `Clear(GenJnlCheckLine)` — [L190-L345](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L190-L345) (grep of that range in this session).
- `CheckLine` → `CheckRecurringLine`, `UpdateRecurringAmt`, `CheckAllocations`, `PostingSetupMgt.ConfirmPostingAfterWorkingDate(ConfirmPostingAfterWorkingDateQst, ...)` (only once per batch), `PrepareGenJnlLineAddCurr`, `GenJnlCheckLine.RunCheck(GenJnlLine5)`, `CheckRestrictions`; the `OnBeforeCheckLine(var GenJnlLine, var PostingAfterWorkingDateConfirmed, var IsHandled)` event lets you pre-confirm — [L1587-L1624](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L1587-L1624)
- `PostGenJournalLine` → `CheckDocumentNo(GenJournalLine)` then `GenJnlLine5.Copy(...)`, `PrepareGenJnlLineAddCurr`, `UpdateIncomingDocument`, `OnBeforePostGenJnlLine`, `GenJnlPostLine.RunWithoutCheck(GenJnlLine5)`, `InsertPostedGenJnlLine`, `RemoveRecordLink`, `UnlinkIncDocFromGenJnlLine` — [L1528-L1551](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L1528-L1551)
- `CheckDocumentNo`: if `"Posting No. Series" = ''` it is set from `GenJnlBatch."No. Series"`; otherwise for non-empty lines the `Document No.` is **replaced** by `NoSeriesBatch.GetNextNo("Posting No. Series", "Posting Date")` unless the line has the same Document No. as the previous line (then it reuses `LastPostedDocNo`) — [L853-L872](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L853-L872)
- `CheckBalance`: errors if `CurrentBalance <> 0`; with `GenJnlTemplate."Force Doc. Balance"` the message references `Document No.`, otherwise it references `Posting Date`; also checks `CurrencyBalance` per currency — [L546-L591](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostBatch.Codeunit.al#L546-L591)
- `procedure SetSuppressCommit(NewSuppressCommit: Boolean)` (L1626) and `procedure SetPreviewMode` (L1361) are public; `OnBeforeCheckLine` is a published event used by Shopify's auto-post codeunit (below).
- Posted lines are archived via `procedure InsertPostedGenJnlLine(GenJournalLine)` (L1662) into `Posted Gen. Journal Line` (table file `PostedGenJournalLine.Table.al` in the same Journal folder).

**Codeunit 12 `RunWithCheck`:**
```al
procedure RunWithCheck(var GenJnlLine2: Record "Gen. Journal Line"): Integer
var
    GenJnlLine: Record "Gen. Journal Line";
    IsHandled: Boolean;
begin
    IsHandled := false;
    OnBeforeRunWithCheck(GenJnlLine, GenJnlLine2, GLEntryNo, IsHandled);
    if IsHandled then
        exit(GLEntryNo);
    if GLReg."No." = 0 then
        SequenceNoMgt.ClearSequenceNoCheck();
    GenJnlLine.Copy(GenJnlLine2);
    Code(GenJnlLine, true);
    OnAfterRunWithCheck(GenJnlLine);
    GenJnlLine2 := GenJnlLine;
    exit(GLEntryNo);
end;
```
— [GenJnlPostLine.Codeunit.al L209-L226](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostLine.Codeunit.al#L209-L226). The XML doc comment on `RunWithoutCheck` says it "posts the journal line without checking it. As a result G/L Entries and Register are created along with other related ledger entries" and returns the "No. of the last General Ledger Entry that has been created" (L228-L234).
- Inside `Code`: empty lines (`GenJnlLine.EmptyLine()`) only update `InitLastDocDate`; `"VAT Reporting Date"` defaults from Posting/Document date; `CheckGenJnlLine(GenJnlLine, CheckLine)`; when the account or bal. account is Customer/Vendor and dates are blank, `"Document Date" := "Posting Date"` and `"Due Date" := "Posting Date"`; `StartPosting` … `FinishPosting` — [L252-L340 grep in this session](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Posting/GenJnlPostLine.Codeunit.al#L252)

**Codeunit 11 `RunCheck` (what a line must satisfy):** `EmptyLine()` lines exit early; `CheckDates`; if `"Bal. Account No." = ''` then `TestField("Account No.")`; `CheckZeroAmount`; `Amount (LCY)` must have the same sign as `Amount`; `CheckAppliesToDocNo`; `CheckAccountNo` if account set; `CheckBalAccountNo` if bal. account set; IC account blocked checks; when neither side is Customer/Vendor: `TestField("Pmt. Discount Date", 0D)`, `TestField("Payment Discount %", 0)`; when neither side is Bank: `TestField("Bank Payment Type", " ")`; when neither side is Fixed Asset: `TestField("Depreciation Book Code", '')`, `TestField("FA Posting Type", 0)`; deferral check; `CheckDimensions`; `CheckCurrencyCode`; cost-accounting dimension check; `TestField("Document No.")` — [GenJnlCheckLine.Codeunit.al L115-L230](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJnlCheckLine.Codeunit.al#L115-L230) (grep in this session).

**Table 81 "Gen. Journal Line" — field numbers and key validate triggers** ([GenJournalLine.Table.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalLine.Table.al), raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalLine.Table.al):
- `field(1; "Journal Template Name"; Code[10])`, `field(2; "Line No."; Integer)`, `field(3; "Account Type"; Enum "Gen. Journal Account Type")`, `field(4; "Account No."; Code[20])`, `field(5; "Posting Date"; Date)`, `field(6; "Document Type"; Enum "Gen. Journal Document Type")`, `field(7; "Document No."; Code[20])`, `field(11; "Bal. Account No."; Code[20])`, `field(12; "Currency Code"; Code[10])`, `field(13; Amount; Decimal)`, `field(14; "Debit Amount")`, `field(15; "Credit Amount")`, `field(16; "Amount (LCY)")`, `field(24/25; "Shortcut Dimension 1/2 Code")`, `field(29; "Source Code")`, `field(35; "Applies-to Doc. Type")`, `field(36; "Applies-to Doc. No.")`, `field(38; "Due Date")`, `field(47; "Payment Terms Code")`, `field(51; "Journal Batch Name"; Code[10])`, `field(52; "Reason Code")`, `field(57; "Gen. Posting Type")`, `field(58/59; "Gen. Bus./Prod. Posting Group")`, `field(63; "Bal. Account Type")`, `field(76; "Document Date")`, `field(77; "External Document No."; Code[35])`, `field(80; "Posting No. Series")`, `field(84; "Tax Group Code")`, `field(90/91; "VAT Bus./Prod. Posting Group")`, `field(128; "VAT Reporting Date")`, `field(172; "Payment Method Code")`, `field(480; "Dimension Set ID")`, `field(8001; "Account Id")`, `field(8002; "Customer Id")`, `field(8003; "Applies-to Invoice Id")`, `field(8006; "Journal Batch Id")`, `field(8008; "Balance Account Id")`, `field(8009; "Vendor Id")` — all from the table file (grep in this session).
- `"Account No."` TableRelation: G/L Account `where("Account Type" = const(Posting), Blocked = const(false))`, Customer, Vendor, Bank Account, Fixed Asset, IC Partner, Allocation Account, Employee; its `OnValidate` clears application if changed, calls `GetGLAccount()/GetCustomerAccount()/GetVendorAccount()/GetEmployeeAccount()/GetBankAccount()/GetFAAccount()/GetICPartnerAccount()/GetAllocationAccount()`, then `Validate("Currency Code")`, `Validate("VAT Prod. Posting Group")`, `UpdateLineBalance()`, `UpdateSource()` and creates default dimensions — [GenJournalLine.Table.al L178-L250](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalLine.Table.al#L178-L250)
- `Amount` OnValidate → `ValidateAmount()`; `"Debit Amount"` OnValidate rounds, sets `Correction := "Debit Amount" < 0` and `Validate(Amount)` — same file around `field(13; Amount; Decimal)`.
- Useful public procedures: `EmptyLine()` (L4165), `UpdateLineBalance()` (L4225), `SetUpNewLine(LastGenJnlLine, Balance, BottomLine)` (L4281), `InitNewLine(PostingDate, DocumentDate, VATDate, PostingDescription, ShortcutDim1Code, ShortcutDim2Code, DimSetID, ReasonCode)` (L4362), `CreateDim(...)` (L5072), `ValidateShortcutDimCode` (L5092), `SetJournalLineFieldsFromApplication()` (L6542), `CopyVATSetupToJnlLines()` (L7473), `SetHideValidation(NewHideValidationDialog)` (L5900), `UpdateAccountID()` (L10945), `UpdateCustomerID()` (L11051), `UpdateAppliesToInvoiceID()` (L11125), `UpdateJournalBatchID()` (L11252).
- `table 232 "Gen. Journal Batch"`: `field(5; "Bal. Account Type")`, `field(6; "Bal. Account No.")`, `field(7; "No. Series")`, `field(8; "Posting No. Series")`, `field(8002; BalAccountId; Guid)`, `procedure SetupNewBatch()` (L381), `procedure UpdateBalAccountId()` (L539) — [GenJournalBatch.Table.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/Finance/GeneralLedger/Journal/GenJournalBatch.Table.al)

**Microsoft's own "create a line programmatically" validation order (Data Migration Facade Helper, codeunit 1797)** — the most authoritative example of field order for opening balances:
```al
GenJournalLine.Init();
GenJournalLine.SetHideValidation(true);
GenJournalLine.Validate("Source Code", GenJournalTemplate."Source Code");
GenJournalLine.Validate("Journal Template Name", GenJournalBatch."Journal Template Name");
GenJournalLine.Validate("Journal Batch Name", GenJournalBatch.Name);
GenJournalLine.Validate("Line No.", LineNum);
GenJournalLine.Validate("Account Type", AccountType);
GenJournalLine.Validate("Document No.", DocumentNo);
GenJournalLine.Validate("Account No.", AccountNo);
GenJournalLine.Validate(Description, Description);
GenJournalLine.Validate("Document Date", PostingDate);
GenJournalLine.Validate("Posting Date", PostingDate);
GenJournalLine.Validate("Due Date", DueDate);
GenJournalLine.Validate(Amount, Amount);
GenJournalLine.Validate("Amount (LCY)", AmountLCY);
GenJournalLine.Validate("Currency Code", DataMigrationFacadeHelper.FixIfLcyCode(Currency));
GenJournalLine.Validate("Bal. Account Type", GenJournalLine."Bal. Account Type"::"G/L Account");
GenJournalLine.Validate("Bal. Account No.", BalancingAccount);
GenJournalLine.Validate("Bal. Gen. Posting Type", GenJournalLine."Bal. Gen. Posting Type"::" ");
GenJournalLine.Validate("Bal. Gen. Bus. Posting Group", '');
GenJournalLine.Validate("Bal. Gen. Prod. Posting Group", '');
GenJournalLine.Validate("Bal. VAT Prod. Posting Group", '');
GenJournalLine.Validate("Bal. VAT Bus. Posting Group", '');
GenJournalLine.Insert(true);
```
— [DataMigrationFacadeHelper.Codeunit.al L262-L304](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/DataMigrationFacadeHelper.Codeunit.al#L262-L304) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/DataMigrationFacadeHelper.Codeunit.al). Line numbers are allocated as `FindLast()."Line No." + 10000` or `10000`.

**Headless posting pattern used by Microsoft (GP migration):**
```al
local procedure SafePostGLBatch(JournalBatchName: Code[10])
var
    GenJournalLine: Record "Gen. Journal Line";
begin
    GenJournalLine.SetRange("Journal Template Name", GeneralTemplateNameTxt);
    GenJournalLine.SetRange("Journal Batch Name", JournalBatchName);
    if GenJournalLine.FindFirst() then begin
        // Commit is required to safely handle errors that may occur during posting.
        Commit();
        if not Codeunit.Run(Codeunit::"Gen. Jnl.-Post Batch", GenJournalLine) then
            LogWarningAndClearLastError(JournalBatchName);
    end;
end;
```
— [HybridGP HelperFunctions.codeunit.al L1396-L1408](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/HybridGP/app/src/Migration/Support/HelperFunctions.codeunit.al#L1396-L1408); `GeneralTemplateNameTxt: Label 'GENERAL'` (L114).
- Shopify's auto-post codeunit (`codeunit 30422 "Shpfy Auto Gen. Jnl.-Post"`) creates an **isolated batch per run** by copying the configured batch with a unique name (`'SHPFY' + 5 chars of a GUID`) and subscribes to `Codeunit::"Gen. Jnl.-Post Batch"`, `'OnBeforeCheckLine'` to set `PostingAfterWorkingDateConfirmed := true` so no dialog is raised — [ShpfyAutoGenJnlPost.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/Shopify/App/src/Transactions/Codeunits/ShpfyAutoGenJnlPost.Codeunit.al)
- Test library usage pattern in the API E2E test: `LibraryERM.CreateGeneralJnlLine(GenJournalLine, TemplateName, BatchName, DocumentType::Invoice, AccountType::Customer, CustomerNo, Amount)` — [APIV2JournalsE2E.Codeunit.al L199-L204](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/test/src/APIV2JournalsE2E.Codeunit.al#L199-L204)

### Inferences
- For an unattended opening-balance poster the robust sequence is: (1) create/lookup a dedicated batch with `Posting No. Series` blank if you want to keep your own Document Nos. (because `CheckDocumentNo` overwrites Document No. whenever `Posting No. Series` is set), (2) build lines using the Facade Helper order, (3) `Commit()`, (4) `Codeunit.Run(Codeunit::"Gen. Jnl.-Post Batch", GenJournalLine)` and capture `GetLastErrorText()` — avoiding codeunit 231 entirely sidesteps the confirm dialogs and the "Post with Job Queue" branch.
- If you must go through codeunit 231 (e.g. you want the same code path as the API `post` action), subscribe to `OnBeforeCode` to set `HideDialog := true`, or rely on the fact that web-service sessions auto-answer `ConfirmManagement.GetResponseOrDefault(..., true)` with the default.
- `GenJnlPostLine.RunWithCheck` is appropriate for single-line, single-transaction postings (e.g. one balanced line with Bal. Account); it bypasses batch-level balance checking and document-number assignment, so the caller must guarantee the line balances (Amount + Bal. Account) or post pairs within one transaction.

### Gaps
- Did not extract the full `ProcessLines` body (L190-L345) verbatim; only the control-flow lines were grepped. Line references are given so the writer can quote further.
- The requester's hypothesis that `"Gen. Posting Type"/VAT fields must be blank` is supported indirectly (the migration helper explicitly blanks the Bal. posting groups, and `SetPostingGroupValues` copies groups only when `CopyVATSetupToJnlLines()`), but no explicit "must be blank" rule was found in codeunit 11; VAT calculation simply follows whatever posting groups the G/L account validation copies.

---

## 3. Microsoft's data-migration framework for opening balances (Data Migration Facade / Mgt. / Wizard, QuickBooks and Dynamics GP migrations)

### Takeaway
BCApps ships the framework in `src/Layers/W1/BaseApp/System/DataMigration/` (**codeunit 6100 "Data Migration Facade"**, **1798 "Data Migration Mgt."**, **1797 "Data Migration Facade Helper"**, **6110 "GL Acc. Data Migration Facade"**, **6111 "Vendor Data Migration Facade"**, **6112 "Customer Data Migration Facade"**, **page 1808 "Data Migration Wizard"**). The QuickBooks (`src/Apps/W1/QBMigration`) and GP (`src/Apps/W1/HybridGP`) migrators create opening customer/vendor transactions as Gen. Journal Lines with **Account Type Customer/Vendor, Document Type Invoice/Payment/Credit Memo, a G/L balancing account = receivables/payables account, posting date = source document date, amount sign negated for payments/credit memos**, and G/L beginning balances as G/L lines with no balancing account; batches are then posted with `Codeunit.Run(Codeunit::"Gen. Jnl.-Post Batch", ...)`. The wizard's "Opening balances" option is `"Post balances for me"` (with a `Post to ledger on` date validated against Accounting Periods) vs `"Review balances first"`.

### Cited Findings
- Framework files present (W1 layer): `DataMigrationFacade.Codeunit.al` (`codeunit 6100 "Data Migration Facade"`, events `OnFindBatchForCustomerTransactions(MigrationType, var GenJournalBatchName)`, `OnFindBatchForVendorTransactions`, `OnFindBatchForAccountTransactions(DataMigrationStatus, var GenJournalBatchName)`), `DataMigrationMgt.Codeunit.al` (`codeunit 1798 "Data Migration Mgt."`; `StartMigration(MigrationType, Retry)`, `RunStagingTableMigrationCodeunit`, `CheckForEntitiesToBePosted()`), `DataMigrationFacadeHelper.Codeunit.al` (`codeunit 1797`), `CustomerDataMigrationFacade.Codeunit.al` (`codeunit 6112`), `VendorDataMigrationFacade.Codeunit.al` (`codeunit 6111`), `GLAccDataMigrationFacade.Codeunit.al` (`codeunit 6110`), `DataMigrationWizard.Page.al` (`page 1808`), `DataMigrationOverview.Page.al`, `DataMigrationStatus.Table.al` — [folder](https://github.com/microsoft/BCApps/tree/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration) (names/IDs verified by grep of each file in this session).
- Customer facade API for transactions: `CreateGeneralJournalBatchIfNeeded(GeneralJournalBatchCode: Code[10]; NoSeriesCode: Code[20]; PostingNoSeriesCode: Code[20])`, `CreateGeneralJournalLine(GeneralJournalBatchCode; DocumentNo; Description; PostingDate; DueDate; Amount; AmountLCY; Currency; BalancingAccount)` (which calls the helper with `"Account Type"::Customer` and `GlobalCustomer."No."`), `SetGeneralJournalLineDimension(...)` (builds a Dimension Set ID and `Modify(true)`), `SetGeneralJournalLineDocumentType(DocumentTypeToSet: Option " ",Payment,Invoice,"Credit Memo","Finance Charge Memo",Reminder,Refund)` (does `Validate("Document Type")` + `Modify(true)`), `SetGeneralJournalLineSourceCode`, `SetGeneralJournalLineExternalDocumentNo`, `SetGeneralJournalLineSalesPersonCode`, `SetGeneralJournalLinePaymentTerms`; integration events `OnMigrateCustomerPostingGroups(RecordIdToMigrate, ChartOfAccountsMigrated)` and `OnMigrateCustomerTransactions(RecordIdToMigrate, ChartOfAccountsMigrated)` — [CustomerDataMigrationFacade.Codeunit.al L91-L165, L527-L534](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/CustomerDataMigrationFacade.Codeunit.al#L91-L165) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/CustomerDataMigrationFacade.Codeunit.al)
- Vendor facade mirrors it and adds `SetGeneralJournalLineBalAccountNo(BalAccountNoToSet)` — [VendorDataMigrationFacade.Codeunit.al L89-L170](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/VendorDataMigrationFacade.Codeunit.al#L89-L170)
- GL facade exposes `CreateGeneralJournalLine(...)` (same signature; `Account Type` G/L) and `CreateGeneralJournalBatchIfNeeded`, plus events `OnCreateOpeningBalanceTrx(RecordIdToMigrate)`, `OnMigratePostingGroups`, `OnMigrateAccountTransactions` — [GLAccDataMigrationFacade.Codeunit.al L34-L52, L132-L161](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/GLAccDataMigrationFacade.Codeunit.al#L34-L52)
- `CreateGeneralJournalBatchIfNeeded` (helper): finds the first `Gen. Journal Template` with `Type = General`, `Recurring = false` (creates one named after the batch code if none), then creates the batch via `Validate("Journal Template Name")`, `SetupNewBatch()`, `Validate(Name)`, `Validate(Description)`, assigns `"No. Series"` and `"Posting No. Series"` **directly** (no Validate), `Insert(true)` — [DataMigrationFacadeHelper.Codeunit.al L224-L260](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/DataMigrationFacadeHelper.Codeunit.al#L224-L260)
- **GP customer opening transactions** (`src/Apps/W1/HybridGP/app/src/Migration/Customers/GPCustomerMigrator.codeunit.al`): subscriber `OnMigrateCustomerTransactions` creates batch `CopyStr(CustomerBatchNameTxt, 1, 7)` where `CustomerBatchNameTxt: Label 'GPCUST'`; loops `GP Customer Transactions` by `TransType` Invoice / Payment / "Credit Memo" and calls
```al
Sender.CreateGeneralJournalLine(
    CopyStr(CustomerBatchNameTxt, 1, 7),
    CopyStr(MigrationGPCustTrans.DOCNUMBR, 1, 20),
    CopyStr(MigrationGPCustomer.CUSTNAME, 1, 50),
    MigrationGPCustTrans.DOCDATE,
    0D,
    MigrationGPCustTrans.CURTRXAM,
    MigrationGPCustTrans.CURTRXAM,
    '',
    ReceivablesAccountNo
);
Sender.SetGeneralJournalLineDocumentType(MigrationGPCustTrans.TransType);
DataMigrationFacadeHelper.CreateSourceCodeIfNeeded(CopyStr(SourceCodeTxt, 1, 10));
Sender.SetGeneralJournalLineSourceCode(CopyStr(SourceCodeTxt, 1, 10));
```
  with payments and credit memos passing `-MigrationGPCustTrans.CURTRXAM`; `SourceCodeTxt: Label 'GENJNL'`, `PostingGroupCodeTxt: Label 'GP'`; due date is passed as `0D` and payment terms set via `SetGeneralJournalLinePaymentTerms(PYMTRMID)` — [GPCustomerMigrator.codeunit.al L21-L23, L77-L180](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/HybridGP/app/src/Migration/Customers/GPCustomerMigrator.codeunit.al#L77-L180) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/HybridGP/app/src/Migration/Customers/GPCustomerMigrator.codeunit.al)
- **GP vendor** does the same with `PayablesAccountNo` from `GetVendorPayablesAccount(...)` / `HelperFunctions.GetPostingAccountNumber('PayablesAccount')` and `SetGeneralJournalLineDocumentType(GPVendorTransactions.TransType)` — [GPVendorMigrator.codeunit.al L82-L200](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/HybridGP/app/src/Migration/Vendors/GPVendorMigrator.codeunit.al#L82-L200)
- **GP G/L beginning balances** (`GPAccountMigrator.codeunit.al`, `procedure CreateBeginningBalance(var GPAccount)` → `CreateGLAccountBeginningBalanceImp`): reads `GP GL10111` with `PERIODID = 0` and `YEAR1 = InitialYear`, batch name `'GP' + Format(InitialYear) + 'BB'`, posting date = `GPFiscalPeriods.PERIODDT` (period 0 of the initial year), **due date `0D`, currency `''`, balancing account `''`** (i.e. a pure G/L line — the batch must balance across accounts), then sets `"Dimension Set ID"` from GP account segments and `Modify(true)` — [GPAccountMigrator.codeunit.al L151-L239](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/HybridGP/app/src/Migration/Accounts/GPAccountMigrator.codeunit.al#L151-L239); subscriber `OnCreateOpeningBalanceTrx` at L129.
- **GP posting of migrated batches**: `procedure PostGLTransactions()` iterates item, G/L, statistical, customer and vendor batches with per-type `OnSkipPosting*` events and `GPCompanyAdditionalSettings.GetSkipAllPosting()`; `SafePostGLBatch` is shown in section 2 — [HelperFunctions.codeunit.al L1287-L1410](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/HybridGP/app/src/Migration/Support/HelperFunctions.codeunit.al#L1287-L1410)
- **QuickBooks customer transactions** (`src/Apps/W1/QBMigration/app/src/Customers/MigrationQBCustomerMigrator.Codeunit.al`): batch `CopyStr(PostingGroupCodeTxt, 1, 5)` with `PostingGroupCodeTxt: Label 'QB'`; for Invoice: `CreateGeneralJournalLine(batch, DocNo, Name, MigrationQBCustTrans.TxnDate, DueDate, Amount, Amount, currency, HelperFunctions.GetPostingAccountNumber('ReceivablesAccount'))`, then `SetGeneralJournalLineDocumentType(TransType)`, `SetGeneralJournalLineSourceCode('GENJNL')`, `SetGeneralJournalLineExternalDocumentNo(DocNumber)`; Payment uses `-Amount` and `SetGeneralJournalLineDocumentType(TransType::Payment)`; Credit Memo uses `-Amount` — [MigrationQBCustomerMigrator.Codeunit.al L50-L110](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/QBMigration/app/src/Customers/MigrationQBCustomerMigrator.Codeunit.al#L50-L110) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/QBMigration/app/src/Customers/MigrationQBCustomerMigrator.Codeunit.al); sibling files `MigrationQBVendorMigrator.Codeunit.al`, `MigrationQBAccountMigrator.Codeunit.al`, `Support/MigrationQBHelperFunctions.Codeunit.al`, `Support/MigrationQBPostingAccounts.Page.al`.
- **Data Migration Wizard (page 1808)** opening-balance UI: `field(BallancesPostingOption; BallancesPostingOption)` with `Caption = 'Opening balances'`, ToolTip "Specifies what to do with opening balances. We can post them for you, or you can review balances in journals and post them yourself."; option `" ","Post balances for me","Review balances first"`; nested `field(PostingDate)` captioned `'Post to ledger on'` (default `WorkDate()`); before applying, `AccountingPeriod.GetFiscalYearStartDate(PostingDate) = 0D` raises `MissingAccountingPeriodeErr`; the choice is passed to the entities sub-page via `CurrPage.DataMigrationEntities.PAGE.SetPostingInfromation(BallancesPostingOption = "Post balances for me", PostingDate)` — [DataMigrationWizard.Page.al L141-L167, L565, L740-L746, L862-L871](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataMigration/DataMigrationWizard.Page.al#L141-L167)
- Microsoft's Dynamics NAV/BC help "Create Journal Opening Balances" (RapidStart): create journal lines with the *Create G/L Journal Lines* action, export to Excel, enter amounts, re-import and post — [LS Retail mirror of Microsoft Docs](https://help.lscentral150.lsretail.com/Content/Dynamics%20NAV/admin-how-to-create-journal-opening-balances.html); [To-Increase mirror](https://business-central.to-increase.com/md/en-US/admin-how-to-create-journal-opening-balances) (search snippets; learn.microsoft.com unreachable).
- MB-800 lab: opening balances imported with a configuration package containing table 81 with dimension columns, then posted in the `OPENING` batch — [microsoftlearning.github.io Lab25](https://microsoftlearning.github.io/MB-800-Business-Central-Functional-Consultant/Instructions/Labs/Lab25_Process_Cash_Management.html) (search snippet).

### Inferences
- Microsoft's canonical opening-balance shape for receivables/payables is **one Gen. Journal Line per open document**, `Account Type = Customer/Vendor`, `Document Type = Invoice` (positive) or `Payment`/`Credit Memo` (negative), `Document No. = source document number`, `Posting Date = source document date`, `Bal. Account Type = G/L Account`, `Bal. Account No. = receivables/payables control account` (so the G/L is net-zero and only the sub-ledger changes), Bal. posting groups blanked to avoid VAT. Due date is either explicit (QB) or left `0D` and derived from payment terms (GP) — codeunit 12 then defaults `Due Date := Posting Date` when blank.
- G/L opening balances are plain G/L lines without a balancing account; the batch must sum to zero (or use an equity/suspense account), and the wizard enforces an open Accounting Period for the posting date.
- The framework's `SetHideValidation(true)` + `Validate` approach, followed by `Modify(true)` for Document Type/dimensions, is a safe template for a custom "opening balance import" codeunit.

### Gaps
- No file literally named "Set up Opening Balances" exists in BCApps; the wizard field is captioned "Opening balances" inside page 1808. A case-insensitive grep for `OpeningBalance` in the full tree returned only the GP migrator event name.
- The `DataMigrationEntities` sub-page's `SetPostingInfromation` and the code that eventually posts "for me" (likely `Data Migration Mgt.`/`Data Migration Status` with `"Post ..."` flags) were not read; file names are given above for follow-up.

---

## 4. Community repositories (StefanMaron history, opening-balance imports, custom journal API pages)

### Takeaway
Very little public AL exists for opening-balance imports; the most relevant community artefacts found are **StefanMaron/MSDyn365BC.Code.History** (branches `w1-24` … `w1-29`, one branch per BC major, for diffing base-app journal code across versions), the tiny **jigneshkhatri/MBC-Gen-Journal-Line-Posting-CodeUnit** (codeunit 50101 exposing `PostGenJournalLine(genJournalLineID: Guid)` as an OData-bound codeunit that runs codeunit 231), the **Stoneridge "General Journal Import" XMLport tutorial**, and the generated **spysystem/msbc-rest** client that documents a custom "SpyJournalPage"/"TempJournalLines + commitToJournalLine" API pattern. No public repo with a full custom API page exposing Document Type / Due Date / Currency / Applies-to on table 81 was found via web search.

### Cited Findings
- StefanMaron/MSDyn365BC.Code.History: "Contains the Microsoft Business Central Code. Updated each month"; README: the repo "holds all versions of the Buisness Central Apps" so you can "quickly be able to compare every version to find changes"; one branch per country and major version (`w1-24`, `w1-23`, `de-24`, …), `main` holds only scripts; recommended clone `git clone -b w1-24 --single-branch` or `--depth 1`; translation files excluded — [github.com/StefanMaron/MSDyn365BC.Code.History](https://github.com/StefanMaron/MSDyn365BC.Code.History). Branches `w1-24 w1-25 w1-26 w1-27 w1-28 w1-29` confirmed via `git ls-remote --heads` in this session.
- jigneshkhatri/MBC-Gen-Journal-Line-Posting-CodeUnit (public, 3 commits, 0 stars): README says publish a web service of Object Type Codeunit, Object ID 50101, then `POST …/ODataV4/<service>_PostGenJournalLine?company=<id>` with body `{"genJournalLineID": "<guid>"}` — [repo page](https://github.com/jigneshkhatri/MBC-Gen-Journal-Line-Posting-CodeUnit). Full source:
```al
codeunit 50101 "Gen. Journal Line Posting"
{
    procedure PostGenJournalLine(genJournalLineID: Guid): Text
    var
        GenJournalLineRec: Record "Gen. Journal Line";
    begin
        // Find the Gen Journal Line based on the provided Guid
        if GenJournalLineRec.GetBySystemId(genJournalLineID) then begin
            // Post the Journal Line
            Codeunit.RUN(Codeunit::"Gen. Jnl.-Post", GenJournalLineRec);
            exit('Gen. Journal Line [Document Type=' + Format(GenJournalLineRec."Document Type") + ', Document No.= ' + GenJournalLineRec."Document No." + '] posted successfully.');
        end
        else begin
            Error('Gen. Journal Line not found.');
        end;
    end;
}
```
  — [raw GenJournalLinePostingCodeunit.al (main)](https://raw.githubusercontent.com/jigneshkhatri/MBC-Gen-Journal-Line-Posting-CodeUnit/main/GenJournalLinePostingCodeunit.al). Note: because codeunit 231 filters by template+batch of the passed record, this posts the **whole batch**, not one line.
- Stoneridge Software, "How to Build a General Journal Import in Business Central" (Daniel Sukup, 28 Feb 2020): builds an XMLport extension that imports a CSV (built in Excel, header removed) into `Gen. Journal Line`, plus a page extension on the General Journal page to launch it — [stoneridgesoftware.com](https://stoneridgesoftware.com/how-to-build-a-general-journal-import-in-business-central/) (search snippet).
- spysystem/msbc-rest (PHP client generated from a BC OpenAPI spec): README lists `BatchApi::callBatchService POST /$batch`, `AuthenticateApi::authenticate POST /token` with `grant_type = 'client_credentials'`, `SpyJournalPageApi` (`POST /SpyJournalPage`, key `('{JournalTemplateName}','{JournalBatchName}',{LineNo})`), and `TempJournalLinesPageApi` with `createTempJournalLine POST /journalLines`, `commitToJournalLine POST /SpyCreateJournalLine_commitToJournalLine`, `commitToJournalLineWithFileData`, `deleteAllTempJournalLines` — [README.md raw](https://raw.githubusercontent.com/spysystem/msbc-rest/master/README.md). This documents a community pattern (stage lines in a temp API page, then one bound action commits them into real journal lines), but the AL side is not in that repo.
- Microsoft's `PageType = API` custom-API sample (`page 50100 "API Car Brand"`: `APIVersion = 'v1.0'; APIPublisher = 'bctech'; APIGroup = 'demo'; EntityName/EntitySetName; ODataKeyFields = SystemId; DelayedInsert = true; Extensible = false`) is the template for a custom journal-line API — [BCTech samples/CustomAPI/APICarBrand.Page.al](https://github.com/microsoft/BCTech/blob/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/CustomAPI/APICarBrand.Page.al) (raw: https://raw.githubusercontent.com/microsoft/BCTech/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/CustomAPI/APICarBrand.Page.al)
- Microsoft Learn "Developing a Custom API" states API pages are created with `PageType = API` and the sample uses `APIPublisher = 'bctech'`, `APIGroup`, `APIVersion`, `EntityName`, `EntitySetName`, `ODataKeyFields = SystemId` — [learn.microsoft.com devenv-develop-custom-api](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-custom-api) (search snippet).
- Microsoft's own `Excel Buffer` table lives at `src/Layers/W1/BaseApp/System/DataExchange/ExcelBuffer.Table.al`, and a base-app test `src/Layers/W1/Tests/ERM/PayrollImportGenJnlTest.Codeunit.al` exercises importing payroll files into Gen. Journal Lines via Data Exchange — [tree listing](https://github.com/microsoft/BCApps/tree/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Layers/W1/BaseApp/System/DataExchange) (paths verified via `git ls-tree`).
- Forum: "API - SaaS 18 insert gen journal balancing account" discusses inserting journal lines with a balancing account through the API — [dynamicsuser.net](https://www.dynamicsuser.net/t/api-saas-18-insert-gen-journal-balancing-account/68850) (search result only; not fetched).

### Inferences
- The practical way to get a "full" journal-line API is to clone page 30049 under your own `APIPublisher/APIGroup`, remove the `OnOpenPage` filters, add `documentType`, `dueDate`, `currencyCode`, `appliesToDocType/No`, `dimensionSetId`/shortcut dims and `customerId`/`vendorId` (table 81 already has fields 8002/8009), and in `OnInsertRecord` reuse `Graph Mgt - Journal Lines.SetJournalLineTemplateAndBatchV2` + `Library API - General Journal.InitializeLine` (both are public base-app procedures), then validate the extra fields in the Facade Helper order. Keep `Codeunit::"Gen. Jnl.-Post"` or `"Gen. Jnl.-Post Batch"` behind a `[ServiceEnabled]` action exactly like page 30016.
- StefanMaron's repo is the fastest way to diff the journal API pages between v24 and v28 if behaviour differences matter (e.g. when `SetJournalLineFiltersV1` widened the account filter).

### Gaps
- No public AL repository implementing an opening-balance import (customer/vendor open items + G/L) was found by WebSearch; searches returned tutorials and Microsoft docs only. GitHub code search was not used per constraints.
- `yzhums.com` and `kauffmann.nl`/`demiliani.com` posts could not be fetched (proxy); their content is therefore not cited except where WebSearch returned a snippet.

---

## 5. Example client code calling `journals` / `journalLines` / `Microsoft.NAV.post` end-to-end (S2S tokens, `$batch`)

### Takeaway
Microsoft's **BCTech** repo provides the S2S token-acquisition building blocks (PowerShell with `Microsoft.Identity.Client` `ConfidentialClientApplicationBuilder … AcquireTokenForClient("https://api.businesscentral.dynamics.com/.default")`, a VS Code REST-client `S2SAccess.rest` with the raw `client_credentials` POST to `login.microsoftonline.com/{tenant}/oauth2/v2.0/token`, and a C# MSAL sample) and the URL shape `https://api.businesscentral.dynamics.com/v2.0/{tenant}/{environment}/api/v2.0/companies(...)`. Transactional `$batch` (`POST .../api/v2.0/$batch` with header `Isolation: snapshot`) is documented by Microsoft (search snippet) and a known-issue article warns of duplicate line numbers when journal lines are inserted concurrently in large batches. No public end-to-end script that creates journal lines and calls `Microsoft.NAV.post` was found.

### Cited Findings
- BCTech `samples/PSOAuthBCAccess/AcquireToken-AsApplication.ps1`:
```powershell
Import-Module ./CommonData.psm1 -Force
Write-Host "Enter the secret for client $ClientId :"
$ClientSecret = Read-Host
# acquire access token as application with client id and secret
$app = [Microsoft.Identity.Client.ConfidentialClientApplicationBuilder]::Create($ClientId).WithClientSecret($ClientSecret).WithTenantId($EntraTenantId).WithAuthority($AuthorityUri).Build()
$AuthenticationResult = $app.AcquireTokenForClient($BcApplicationScopes).ExecuteAsync().GetAwaiter().GetResult()
# use access token to call BC web service
$BcResponse = Invoke-BCWebService -RequestUrl $SampleBCS2SUrl -AccessToken $AuthenticationResult.AccessToken
```
  — [raw](https://raw.githubusercontent.com/microsoft/BCTech/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/PSOAuthBCAccess/AcquireToken-AsApplication.ps1); `CommonData.psm1` defines `$BcAppIdUri = "https://api.businesscentral.dynamics.com"`, `$BcApplicationScopes = @("$BcAppIdUri/.default")`, `$AuthorityUri = "https://login.microsoftonline.com/$EntraTenantId"`, `$SampleBCS2SUrl = "$BcBaseUri/v2.0/$EntraTenantId/$BcEnvironmentName/api/v2.0/companies"`, and `Invoke-RestMethod -Uri $RequestUrl -Headers @{ Authorization = "Bearer $AccessToken" }` — [raw CommonData.psm1](https://raw.githubusercontent.com/microsoft/BCTech/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/PSOAuthBCAccess/CommonData.psm1)
- BCTech `samples/VSCRestClientOAuthBCAccess/S2SAccess.rest`:
```http
@baseUri = https://api.businesscentral.dynamics.com
@scope = {{baseUri}}/.default
@url = {{baseUri}}/v2.0/{{bcEnvironmentName}}/api/v2.0

# @name auth
POST https://login.microsoftonline.com/{{tenantId}}/oauth2/v2.0/token HTTP/1.1
Content-type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={{clientId}}
&client_secret={{clientSecret}}
&scope={{scope}}

@accessHeader = Bearer {{auth.response.body.$.access_token}}
# @name GetCompanies
GET {{url}}/companies HTTP/1.1
Authorization: {{accessHeader}}
@companyId = {{GetCompanies.response.body.value.[0].id}}
@companyUrl = {{url}}/companies({{companyId}})
```
  — [raw S2SAccess.rest](https://raw.githubusercontent.com/microsoft/BCTech/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/VSCRestClientOAuthBCAccess/S2SAccess.rest)
- BCTech `samples/CSharpOAuthBCAccess/DemoBCAccessMSAL/Program.cs` uses `Microsoft.Identity.Client` with `PublicClientApplicationBuilder` and scope `https://api.businesscentral.dynamics.com/Financials.ReadWrite.All` (interactive/delegated, **not** client-credentials) — [raw Program.cs](https://raw.githubusercontent.com/microsoft/BCTech/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/CSharpOAuthBCAccess/DemoBCAccessMSAL/Program.cs). An AL-side OAuth sample exists at `samples/OAuth2Flows/APICalls.Codeunit.al` (`procedure CreateRequest(RequestUrl: Text; AccessToken: Text): Text` using `HttpClient`) — [raw](https://raw.githubusercontent.com/microsoft/BCTech/ccb6c3d36f72b784fb9757316f6f296f0a58ea71/samples/OAuth2Flows/APICalls.Codeunit.al). BCTech sample folders seen: `AdminCenterApi, APIQueryGenerator, CustomAPI, ReturnOfTheComplexType, VisionAPI, CSharpOAuthBCAccess, PSOAuthBCAccess, VSCRestClientOAuthBCAccess, OAuth2Flows, BcMCPProxyPython` — [BCTech samples](https://github.com/microsoft/BCTech/tree/master/samples). No Postman collection or journal sample is in BCTech.
- Microsoft Q&A: the token scope must be `https://api.businesscentral.dynamics.com/.default`; using a Graph scope produced rejected-credentials errors — [learn.microsoft.com/answers 1631653](https://learn.microsoft.com/en-us/answers/questions/1631653/graph-api-to-access-business-central-using-applica) (search snippet).
- Transactional `$batch`: "transactional `$batch` support dates to Business Central 2020 release wave 2 (version 17.1). Adding the `Isolation: snapshot` header to the `$batch` request turns on transactional behavior. The batch then runs in one session, and if the AL code never calls COMMIT, the whole batch shares one transaction… if an inner request fails after earlier requests have committed, the batch's changes are reverted, unless a COMMIT was invoked"; example endpoint `api/v2.0/$batch` — [learn.microsoft.com use-odata-batch](https://learn.microsoft.com/en-ca/dynamics365/business-central/dev-itpro/webservices/use-odata-batch) (search snippet; page not fetched).
- Known issue KA-24233: in large batches (roughly 2,000–30,000 transactions) two journal-line requests can intermittently receive the same `Line No.`, one failing with a duplicate-line error; workaround: avoid concurrent submission and pause between batches — [community.dynamics.com KA-24233](https://community.dynamics.com/article/KA-24233) (search snippet).
- Stefano Demiliani, "Batch API calls and max number of operations" (12 Jan 2021) — exists but could not be fetched (proxy) — [demiliani.com](https://demiliani.com/2021/01/12/dynamics-365-business-central-batch-api-calls-and-max-number-of-operations/)
- Third-party connector guide notes "Business Central posts at the batch level, so all lines in a journal batch are posted together" and recommends isolating unrelated entries in their own batches — [developers.apideck.com guide](https://developers.apideck.com/guides/journal-entries-expenses-mbc) (search snippet).
- Python: `bc-cli` on PyPI is an alpha, unaffiliated SDK showing tenant/client-id/secret auth but no journal writes — [pypi.org/project/bc-cli](https://pypi.org/project/bc-cli/) (search snippet).

### Inferences
- An end-to-end script for opening balances is: (1) `client_credentials` token with scope `https://api.businesscentral.dynamics.com/.default` (the Entra app must be registered in BC's *Microsoft Entra Applications* page with permission sets — not verified here), (2) `GET …/api/v2.0/companies`, (3) `POST …/companies({id})/journals` with `{"code": "OPENBAL", "displayName": "...", "balancingAccountId": "<G/L SystemId>"}` (names from page 30016), (4) `POST …/journals({journalId})/journalLines` per line (or `$batch` with `Isolation: snapshot`, sequential, modest size per KA-24233), with `lineNumber` supplied explicitly to avoid the duplicate-line race, (5) `POST …/journals({journalId})/Microsoft.NAV.post` expecting 204, (6) verify via `generalLedgerEntries`/`customerLedgerEntries`. Because the standard entity cannot set Document Type/Due Date, steps 3-4 must target a custom API for AR/AP opening items.
- The BC server-side `post` action runs codeunit 231 inside the web-service session; `Confirm` dialogs are auto-answered with their defaults there, which is why `ConfirmManagement.GetResponseOrDefault(Text001, true)` returns true unattended.

### Gaps
- No public C#, Python, PowerShell or Postman artefact that performs the full create-lines-then-`Microsoft.NAV.post` sequence was found; BCTech only covers token acquisition and generic GETs.
- The Microsoft `$batch` page and Demiliani's batch-limit post were not fetched (proxy block), so exact limits (e.g. max operations per batch, `ODataServicesOperationTimeout`) are not captured.

---

## 6. BCApps test codeunits that document accepted request shapes for the journals API

### Takeaway
`codeunit 139827 "APIV2 - Journals E2E"` (`src/Apps/W1/APIV2/test/src/APIV2JournalsE2E.Codeunit.al`) and `"APIV2 - Customer Payments E2E"` document the JSON keys (`code`, `displayName`, `balancingAccountId`; line keys built by `LibraryGraphJournalLines.CreateLineWithGenericLineValuesJSON(LineNo, Amount)` plus `customerNumber`, `appliesToInvoiceNumber`/`appliesToInvoiceId`) and prove that `journals({id})/Microsoft.NAV.post` returns **204 with an empty body** and posts Customer/Invoice lines that were created in AL.

### Cited Findings
- `codeunit 139827 "APIV2 - Journals E2E"`, `ServiceNameTxt: Label 'journals'`; tests `TestCreateJournal`, `TestGetJournals`, `TestModifyJournal`, `TestDeleteJournal`, `TestActionPostGenJournalBatch` — [APIV2JournalsE2E.Codeunit.al](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/test/src/APIV2JournalsE2E.Codeunit.al) (raw: https://raw.githubusercontent.com/microsoft/BCApps/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/test/src/APIV2JournalsE2E.Codeunit.al)
- Journal create body (keys `JournalNameTxt`, `JournalDescriptionNameTxt`, `JournalBalAccountIdTxt`; the balancing account is sent as the G/L account's `SystemId` lower-cased, `Format(GLAccount.SystemId, 0, 4)`) — `CreateJournalJSON` at L225-L240.
- Post action test:
```al
CreateGeneralJournalBatch(GenJournalBatch, BalAccountType, BalAccountNo);
LibraryERM.CreateGeneralJnlLine(GenJournalLine, GenJournalBatch."Journal Template Name", GenJournalBatch.Name,
  GenJournalLine."Document Type"::Invoice, GenJournalLine."Account Type"::Customer, CustomerNo, Amount);
LibraryERM.CreateGeneralJnlLine(GenJournalLine2, GenJournalBatch."Journal Template Name", GenJournalBatch.Name,
  GenJournalLine."Document Type"::Invoice, GenJournalLine."Account Type"::Customer, Customer2No, Amount2);
GenJournalBatchId := GenJournalBatch.SystemId;
Commit();
// [WHEN] A POST request is made to the API.
TargetURL :=
  LibraryGraphMgt.CreateTargetURLWithSubpage(GenJournalBatchId, Page::"APIV2 - Journals", ServiceNameTxt, ActionPostTxt);
LibraryGraphMgt.PostToWebServiceAndCheckResponseCode(TargetURL, '', ResponseText, 204);
// [THEN] Response should be empty
Assert.AreEqual('', ResponseText, NotEmptyResponseErr);
// [THEN] The general journal line is posted
CustLedgerEntry.SetRange("Customer No.", CustomerNo);
```
  — [APIV2JournalsE2E.Codeunit.al L177-L222](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/test/src/APIV2JournalsE2E.Codeunit.al#L177-L222)
- Customer Payments E2E (`APIV2CustomerPaymentsE2E.Codeunit.al`, 809 lines) builds bodies with `LibraryGraphJournalLines.CreateLineWithGenericLineValuesJSON(LineNo, Amount)` then `AddPropertytoJSON(LineJSON, CustomerNoNameTxt, CustomerNo)`, `AddPropertytoJSON(LineJSON, AppliesToDocNoNameTxt, AppliesToDocNo)`, or `AppliesToInvoiceIdTxt` with `StripBrackets(Format(SalesInvoiceAggregator.GetSalesInvoiceHeaderId(...)))`; a `lineNumber` complex-type test at L119 — [APIV2CustomerPaymentsE2E.Codeunit.al L60-L66, L160-L165, L213](https://github.com/microsoft/BCApps/blob/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV2/test/src/APIV2CustomerPaymentsE2E.Codeunit.al#L60-L66)
- Older v1.0 equivalents also exist: `src/Apps/W1/APIV1/test/src/APIV1JournalLinesE2E.Codeunit.al` and `APIV1CustomerPaymentsE2E.Codeunit.al` — [APIV1 test folder](https://github.com/microsoft/BCApps/tree/9f954e85cbed82e2c18b77d8513c22a7d2b2e035/src/Apps/W1/APIV1/test/src)
- No `APIV2JournalLinesE2E.Codeunit.al` file exists in the v2 test folder at this commit; journal-line coverage lives in the v1 test and in the shared `Library - Graph Journal Lines` test library referenced by the customer-payments test (library source not fetched).

### Inferences
- The test confirms the exact URL builder: `CreateTargetURLWithSubpage(batchSystemId, Page::"APIV2 - Journals", 'journals', 'Microsoft.NAV.post')`, i.e. `…/journals({systemId})/Microsoft.NAV.post`, and that the batch SystemId (not the batch code) is the key.
- Because the lines in the posting test are Customer/Invoice lines created in AL, the `post` action is agnostic to how lines were created — a custom API page or an AL import can fill the batch and the standard action can post it.

### Gaps
- The `Library - Graph Journal Lines` test library (which defines the generic line JSON keys) and `LibraryGraphMgt.CreateTargetURLWithSubpage` were not fetched; their file paths were not located in the tree search performed (search was limited to the patterns listed above).
