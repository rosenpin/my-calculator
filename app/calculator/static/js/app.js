(() => {
  const entryEl = document.getElementById("entry");
  const operationEl = document.getElementById("operation");
  const logEl = document.getElementById("log");
  const clockEl = document.getElementById("live-clock");

  let buffer = "0";
  let storedValue = null;
  let operator = null;
  let resetOnDigit = false;

  const updateEntry = (value) => {
    entryEl.textContent = value;
  };

  const updateOperation = (text) => {
    operationEl.textContent = text;
  };

  const appendLog = (message, status = "ok") => {
    const li = document.createElement("li");
    li.textContent = message;
    if (status !== "ok") {
      li.style.borderLeftColor = "#ef476f";
    }
    logEl.prepend(li);
    const maxEntries = 10;
    while (logEl.childElementCount > maxEntries) {
      logEl.removeChild(logEl.lastChild);
    }
  };

  const resetCalculator = () => {
    buffer = "0";
    storedValue = null;
    operator = null;
    resetOnDigit = false;
    updateEntry(buffer);
    updateOperation("Ready");
  };

  const pushDigit = (digit) => {
    if (resetOnDigit) {
      buffer = digit === "." ? "0." : digit;
      resetOnDigit = false;
      updateEntry(buffer);
      return;
    }

    if (digit === "." && buffer.includes(".")) {
      return;
    }

    if (buffer === "0" && digit !== ".") {
      buffer = digit;
    } else {
      buffer += digit;
    }
    updateEntry(buffer);
  };

  const applySign = () => {
    if (buffer.startsWith("-")) {
      buffer = buffer.substring(1);
    } else if (buffer !== "0") {
      buffer = `-${buffer}`;
    }
    updateEntry(buffer);
  };

  const applyPercent = () => {
    const value = parseFloat(buffer);
    if (!Number.isNaN(value)) {
      buffer = (value / 100).toString();
      updateEntry(buffer);
    }
  };

  const setOperator = (symbol) => {
    if (operator && !resetOnDigit) {
      performCalculation();
    }
    storedValue = buffer;
    operator = symbol;
    resetOnDigit = true;
    updateOperation(`${storedValue} ${operator}`);
  };

  const performCalculation = async () => {
    if (storedValue === null || operator === null) {
      return;
    }
    const payload = {
      left: storedValue,
      right: buffer,
      operator,
    };

    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok || data.status !== "ok") {
        throw new Error(data.message || "Calculation failed");
      }

      buffer = data.result.toString();
      appendLog(
        `${data.left} ${data.operator} ${data.right} = ${data.result} (${data.evaluated_at})`
      );
      updateEntry(buffer);
      updateOperation("Ready");
      storedValue = null;
      operator = null;
      resetOnDigit = true;
    } catch (error) {
      appendLog(error.message, "error");
      updateOperation("Error");
      resetOnDigit = true;
    }
  };

  const handleKeyPress = (event) => {
    const { value } = event.currentTarget.dataset;
    const action = event.currentTarget.dataset.action;

    if (value) {
      if (["+", "-", "×", "÷"].includes(value)) {
        setOperator(value);
      } else {
        pushDigit(value);
      }
      return;
    }

    switch (action) {
      case "equals":
        performCalculation();
        break;
      case "clear":
        resetCalculator();
        break;
      case "sign":
        applySign();
        break;
      case "percent":
        applyPercent();
        break;
      default:
        break;
    }
  };

  const bindKeys = () => {
    const keys = document.querySelectorAll(".key");
    keys.forEach((key) => key.addEventListener("click", handleKeyPress));
  };

  const updateClock = async () => {
    try {
      const response = await fetch("/api/time");
      if (!response.ok) {
        throw new Error("Clock update failed");
      }
      const { iso } = await response.json();
      const parsed = new Date(iso);
      clockEl.textContent = parsed.toLocaleTimeString();
    } catch (error) {
      clockEl.textContent = "--:--:--";
    }
  };

  const init = () => {
    bindKeys();
    resetCalculator();
    updateClock();
    setInterval(updateClock, 5000);
  };

  document.addEventListener("DOMContentLoaded", init);
})();
