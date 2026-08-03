"use client";

import { useEffect, useMemo, useState } from "react";

type Chunk = {
  rank: number;
  score: number;
  doc: string;
  chunk: number;
  relevant: boolean;
  preview: string;
};

type Benchmark = {
  id: number;
  kind: string;
  query: string;
  gold: string;
  expected: string;
  evidence: string[];
  score: number;
  chunks: Chunk[];
  unfiltered?: Chunk[];
  agentAnswer: string;
  analysis: string;
  fix: string;
};

const benchmarks: Benchmark[] = [
  {
    id: 1,
    kind: "Số liệu + Filter",
    query: "Đối với sinh viên đại học và sau đại học, hạn mức mượn, thời hạn mượn, số lần và thời lượng gia hạn là bao nhiêu?",
    gold: "25 tài liệu trong 30 ngày; gia hạn 1 lần thêm 15 ngày, tối đa 45 ngày, nếu chưa quá hạn và không bị đặt giữ.",
    expected: "rmit-library-borrowing-returning · chunks 3–4",
    evidence: ["Loan quota - 25 items", "Renewals last 15 days"],
    score: 2,
    chunks: [
      { rank: 1, score: 0.6089, doc: "rmit-library-borrowing-returning", chunk: 3, relevant: true, preview: "Borrowing for students… Loan quota - 25 items; loan period - 30 days; renewals - 1." },
      { rank: 2, score: 0.5027, doc: "rmit-library-borrowing-returning", chunk: 6, relevant: true, preview: "Items can be renewed when not overdue or reserved. Renewals last 15 days; maximum renewal period is 45 days." },
      { rank: 3, score: 0.4708, doc: "rmit-library-borrowing-returning", chunk: 4, relevant: true, preview: "Renewals - 1. Items can be renewed online, by phone or in person. Renewals last 15 days." },
    ],
    unfiltered: [
      { rank: 1, score: 0.6089, doc: "rmit-library-borrowing-returning", chunk: 3, relevant: true, preview: "Borrowing for students… Loan quota - 25 items; loan period - 30 days; renewals - 1." },
      { rank: 2, score: 0.5027, doc: "rmit-defer-payment", chunk: 8, relevant: false, preview: "Payment extension conditions include unpaid debt and ability to make full payment within 45 days." },
      { rank: 3, score: 0.4708, doc: "rmit-fees-payments", chunk: 4, relevant: false, preview: "The Student Fees and Charges Guide explains tuition and non-academic fees for the academic year." },
    ],
    agentAnswer: "Context chứa đủ hạn mức 25 tài liệu, thời hạn 30 ngày và quy định gia hạn 1 lần thêm 15 ngày.",
    analysis: "Filter giữ cả ba vị trí cho đúng tài liệu thư viện; không filter thì hai vị trí bị lẫn tài liệu thanh toán. Hai evidence marker đều có trong top-3 và evidence đầu tiên đứng top-1.",
    fix: "Giữ metadata filter audience=all cho truy vấn này; có thể làm sạch navigation để tăng thêm độ chính xác.",
  },
  {
    id: 2,
    kind: "Điều kiện",
    query: "Sinh viên cần đáp ứng những điều kiện nào để được xin gia hạn thanh toán cho Standard Course?",
    gold: "Không ở học kỳ đầu; nợ cũ dưới 5 triệu; chứng minh hoàn cảnh bất ngờ và khả năng trả đủ trong tối đa 45 ngày; tuân thủ các hạn gia hạn trước.",
    expected: "rmit-defer-payment · chunks 7–8",
    evidence: ["less than five million VND", "no more than 45 days"],
    score: 0,
    chunks: [
      { rank: 1, score: 0.6334, doc: "rmit-defer-payment", chunk: 16, relevant: false, preview: "Proof of capacity to pay, such as pay slips, term deposit, bank statements or a finance guarantee." },
      { rank: 2, score: 0.6045, doc: "rmit-defer-payment", chunk: 4, relevant: false, preview: "RMIT has strict payment deadlines but may approve a plan for continuing students in exceptional circumstances." },
      { rank: 3, score: 0.5924, doc: "rmit-fees-payments", chunk: 4, relevant: false, preview: "The Student Fees and Charges Guide explains how fees and charges are set." },
    ],
    agentAnswer: "Không đủ hai điều kiện định lượng trong context để trả lời đầy đủ.",
    analysis: "Hai kết quả đầu đúng tài liệu nhưng sai section. Similarity cao chỉ cho thấy gần chủ đề, không chứng minh chunk chứa điều kiện cần trả lời.",
    fix: "Thử heading-aware chunking, gắn lại heading vào chunk con và tăng overlap quanh danh sách điều kiện.",
  },
  {
    id: 3,
    kind: "Quy trình",
    query: "Muốn hủy toàn bộ đăng ký chương trình, sinh viên phải nộp biểu mẫu nào và ở đâu?",
    gold: "Hoàn thành Program Cancellation form trong mục Submit Request của myRMIT.",
    expected: "rmit-change-cancel-enrolment · chunk 10",
    evidence: ["Program Cancellation form"],
    score: 2,
    chunks: [
      { rank: 1, score: 0.5974, doc: "rmit-change-cancel-enrolment", chunk: 10, relevant: true, preview: "Complete the Program Cancellation form in the Submit Request tile in myRMIT." },
      { rank: 2, score: 0.5472, doc: "rmit-change-cancel-enrolment", chunk: 5, relevant: false, preview: "If you wish to withdraw completely from your studies, you must cancel your program enrolment." },
      { rank: 3, score: 0.5234, doc: "rmit-change-cancel-enrolment", chunk: 3, relevant: false, preview: "You can vary your enrolment until the relevant cut-off dates for adding or dropping courses." },
    ],
    agentAnswer: "Hoàn thành Program Cancellation form tại Submit Request trong myRMIT.",
    analysis: "Chunk chứa đúng biểu mẫu và nơi nộp đứng top-1. Agent có đủ context để trả lời và truy vết về đúng file.",
    fix: "Không cần sửa cho query này; dùng nó làm success case trong demo.",
  },
  {
    id: 4,
    kind: "Liệt kê",
    query: "Thẻ sinh viên RMIT có thể được sử dụng cho những mục đích nào?",
    gold: "Mượn tài liệu; in/scan/photocopy; vào khu vực an ninh; xác minh tại kỳ đánh giá và điểm dịch vụ; nhận ưu đãi.",
    expected: "rmit-student-cards · chunks 3–4",
    evidence: ["print, scan and photocopy", "access secure areas"],
    score: 0,
    chunks: [
      { rank: 1, score: 0.5797, doc: "rmit-student-support", chunk: 6, relevant: false, preview: "RMIT provides blended learning experiences, a supportive community and real-world skills." },
      { rank: 2, score: 0.5530, doc: "rmit-student-support", chunk: 0, relevant: false, preview: "Student support · RMIT University · Students · Library · New students · Campus information." },
      { rank: 3, score: 0.5518, doc: "rmit-defer-payment", chunk: 4, relevant: false, preview: "RMIT may approve payment plans for continuing students in exceptional circumstances." },
    ],
    agentAnswer: "Không có evidence về công dụng thẻ sinh viên trong top-3.",
    analysis: "Cả ba kết quả đều sai tài liệu hoặc sai section; hai evidence marker không xuất hiện. Đây là lỗi recall rõ ràng của retrieval.",
    fix: "Làm sạch menu/footer và thử heading-aware chunker để tiêu đề Student card uses đi cùng nội dung.",
  },
  {
    id: 5,
    kind: "Ngoại lệ",
    query: "Nếu hủy đăng ký sau Census Date nhưng không tham gia lớp học, sinh viên có còn phải trả học phí và các khoản phí khác không?",
    gold: "Có. Sinh viên vẫn phải chịu học phí và các khoản phí khác dù không tham gia lớp học.",
    expected: "rmit-change-cancel-enrolment · chunk 9",
    evidence: ["still liable for tuition and other fees"],
    score: 2,
    chunks: [
      { rank: 1, score: 0.5777, doc: "rmit-change-cancel-enrolment", chunk: 9, relevant: true, preview: "If you cancel after the Census Date, you are still liable for tuition and other fees, even if you do not attend classes." },
      { rank: 2, score: 0.5027, doc: "rmit-change-cancel-enrolment", chunk: 11, relevant: false, preview: "Failure to meet enrolment requirements, non-payment, visa conditions and academic integrity." },
      { rank: 3, score: 0.4947, doc: "rmit-defer-payment", chunk: 5, relevant: false, preview: "Incomplete or late applications will not be assessed; outcomes are sent to the student email account." },
    ],
    agentAnswer: "Có. Sau Census Date, sinh viên vẫn chịu học phí và các khoản phí khác dù không tham gia lớp.",
    analysis: "Ngoại lệ cần tìm xuất hiện nguyên vẹn ở top-1, nên context vừa đủ và câu trả lời được grounding trực tiếp.",
    fix: "Không cần sửa cho query này; giữ làm ví dụ về chunk coherence tốt.",
  },
];

export default function Home() {
  const [selectedId, setSelectedId] = useState(1);
  const [filterOn, setFilterOn] = useState(true);
  const selected = benchmarks[selectedId - 1];
  const activeChunks = selected.id === 1 && !filterOn ? selected.unfiltered! : selected.chunks;
  const totalScore = benchmarks.reduce((sum, item) => sum + item.score, 0);
  const activeScore = selected.id === 1 && !filterOn ? 1 : selected.score;
  const uniqueDocs = useMemo(() => new Set(activeChunks.map((chunk) => chunk.doc)).size, [activeChunks]);
  const evidenceFound = selected.evidence.filter((marker) =>
    activeChunks.some((chunk) => chunk.relevant && chunk.preview.toLocaleLowerCase().includes(marker.toLocaleLowerCase())),
  ).length;

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight") setSelectedId((value) => Math.min(5, value + 1));
      if (event.key === "ArrowLeft") setSelectedId((value) => Math.max(1, value - 1));
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  const enterFullscreen = () => document.documentElement.requestFullscreen?.();

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">C2</span><div><p className="eyebrow">LAB 7 · VECTOR RETRIEVAL</p><h1>Benchmark Observatory</h1></div></div>
        <div className="header-actions"><span className="status-dot"><i /> Local model ready</span><button className="present-button" onClick={enterFullscreen}>Trình chiếu ↗</button></div>
      </header>

      <section className="hero-strip">
        <div><p className="eyebrow accent">RMIT UNIVERSITY SERVICES</p><h2>Local embedding: từ mock 0/10 lên 6/10</h2></div>
        <div className="metric-row"><Metric value="7" label="tài liệu" /><Metric value="103" label="chunks" /><Metric value="5" label="queries khóa" /><Metric value={`${totalScore}/10`} label="local benchmark" tone="success" /></div>
      </section>

      <div className="workspace">
        <aside className="query-rail">
          <div className="rail-heading"><span>Benchmark set</span><b>{selected.id} / {benchmarks.length}</b></div>
          <div className="progress-track"><span style={{ width: `${selected.id * 20}%` }} /></div>
          <nav aria-label="Chọn benchmark query">
            {benchmarks.map((item) => <button key={item.id} className={`query-button ${selectedId === item.id ? "active" : ""}`} onClick={() => { setSelectedId(item.id); setFilterOn(true); }}><span className="query-index">0{item.id}</span><span><b>{item.kind}</b><small>{item.query}</small></span><em>{item.score}/2</em></button>)}
          </nav>
          <div className="strategy-card"><p className="eyebrow">STRATEGY RIÊNG</p><strong>Recursive · 400</strong><span>paraphrase-multilingual-MiniLM-L12-v2</span><small>↳ local multilingual · normalized vectors</small></div>
        </aside>

        <section className="results-panel">
          <div className="query-header"><div><div className="tag-row"><span className="kind-tag">{selected.kind}</span><span className="query-no">QUERY 0{selected.id}</span></div><h3>{selected.query}</h3></div>{selected.id === 1 && <label className="filter-control"><span><b>Metadata filter</b><small>audience = all</small></span><input type="checkbox" checked={filterOn} onChange={(event) => setFilterOn(event.target.checked)} /><i /></label>}</div>
          {selected.id === 1 && <div className="ab-banner"><span>A/B RESULT</span><p>{filterOn ? "Có filter: 1 document / 3 chunks" : "Không filter: 3 documents / 3 chunks"}</p><b>{uniqueDocs === 1 ? "Nhiễu tài liệu ↓" : "Nhiễu tài liệu ↑"}</b></div>}
          <div className="section-label"><span>TOP-3 RETRIEVAL</span><small>similarity ↓ · evidence check</small></div>
          <div className="chunk-list">{activeChunks.map((chunk) => <article className="chunk-card" key={`${chunk.rank}-${chunk.doc}-${chunk.chunk}`}><div className="rank">#{chunk.rank}</div><div className="chunk-body"><div className="chunk-meta"><code>{chunk.doc}</code><span>/ chunk_{chunk.chunk}</span></div><p>{chunk.preview}</p></div><div className="chunk-score"><strong>{chunk.score.toFixed(4)}</strong><span className={chunk.relevant ? "relevant" : "irrelevant"}>{chunk.relevant ? "Relevant" : "No evidence"}</span></div></article>)}</div>
          <div className="evidence-box"><div><span className="section-label simple">EVIDENCE MARKERS</span>{selected.evidence.map((marker) => <code key={marker}>“{marker}”</code>)}</div><div className="evidence-result"><strong>{evidenceFound}/{selected.evidence.length}</strong><span>xuất hiện trong top-3</span></div></div>
        </section>

        <aside className="analysis-panel">
          <div className={`score-orb ${activeScore === 2 ? "pass" : ""}`}><span>RUBRIC SCORE</span><strong>{activeScore}<small>/2</small></strong><em>{activeScore === 2 ? "PASS" : activeScore === 1 ? "PARTIAL" : "FAILURE"}</em></div>
          <section><p className="eyebrow">GOLD ANSWER</p><blockquote>{selected.gold}</blockquote><div className="expected"><span>Expected</span><code>{selected.expected}</code></div></section>
          <section><p className="eyebrow">AGENT OUTPUT</p><div className="agent-answer"><span>[OFFLINE EXTRACTIVE]</span><p>{selected.agentAnswer}</p></div></section>
          <section className="failure-card"><p className="eyebrow">{activeScore === 2 ? "RESULT ANALYSIS" : "FAILURE ANALYSIS"}</p><p>{selected.analysis}</p><div><b>Đề xuất</b><span>{selected.fix}</span></div></section>
        </aside>
      </div>

      <footer><span>← → chuyển query</span><p><b>Insight:</b> score cao là tín hiệu xếp hạng, không phải bằng chứng nội dung đúng.</p><span>Nhóm C2 · 2026</span></footer>
    </main>
  );
}

function Metric({ value, label, tone }: { value: string; label: string; tone?: string }) {
  return <div className={`metric ${tone ?? ""}`}><strong>{value}</strong><span>{label}</span></div>;
}
