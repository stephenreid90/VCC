async function runDCF() {
  const payload = {
    model_type: "dcf",
    assumptions: {
      fcf_base: parseFloat(document.getElementById("fcf_base").value) * 1e9,
      fcf_growth_rate: parseFloat(document.getElementById("fcf_growth").value),
      wacc: parseFloat(document.getElementById("wacc").value),
      terminal_growth: parseFloat(document.getElementById("tg").value),
      net_debt: parseFloat(document.getElementById("net_debt").value) * 1e9,
      shares_outstanding: parseFloat(document.getElementById("shares").value),
    }
  };
  const res = await fetch("/playground/valuations/api/valuations/calculate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  document.getElementById("result").textContent = JSON.stringify(data, null, 2);
}
