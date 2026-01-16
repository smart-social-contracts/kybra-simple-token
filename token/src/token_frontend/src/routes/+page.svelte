<script>
  import "../index.scss";
  import { backend } from "$lib/canisters";
  import { Principal } from "@dfinity/principal";
  import { onMount, onDestroy } from "svelte";
  import { Chart, PieController, ArcElement, Tooltip, Legend } from "chart.js";

  Chart.register(PieController, ArcElement, Tooltip, Legend);

  let tokenName = "Loading...";
  let tokenSymbol = "";
  let totalSupply = "Loading...";
  let decimals = 8;
  let loading = true;
  let error = null;

  let testMode = false;
  let myPrincipal = "";
  let mintRecipient = "";
  let mintAmount = "";
  let minting = false;
  let mintResult = null;
  let mintError = null;

  let distributionLoading = true;
  let distributionError = null;
  let holderCount = 0;
  let chartCanvas;
  let chart = null;

  const CHART_COLORS = [
    "#4ade80", "#60a5fa", "#f472b6", "#fbbf24", "#a78bfa",
    "#34d399", "#fb7185", "#38bdf8", "#facc15", "#c084fc",
  ];

  function formatSupply(supply, dec) {
    const value = Number(supply) / Math.pow(10, dec);
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  function parseAmount(amountStr, dec) {
    const value = parseFloat(amountStr);
    if (isNaN(value) || value <= 0) {
      return null;
    }
    return BigInt(Math.floor(value * Math.pow(10, dec)));
  }

  function truncateAddress(address) {
    if (address.length <= 16) return address;
    return `${address.slice(0, 8)}...${address.slice(-6)}`;
  }

  async function refreshTokenInfo() {
    const info = await backend.get_token_info();
    totalSupply = formatSupply(info.total_supply, decimals);
  }

  async function loadDistribution() {
    distributionLoading = true;
    distributionError = null;

    try {
      const distribution = await backend.get_token_distribution();
      holderCount = Number(distribution.holder_count);
      const total = Number(distribution.total_supply);

      if (distribution.holders.length === 0) {
        distributionLoading = false;
        return;
      }

      const TOP_N = 8;
      const holders = distribution.holders;
      let chartData = [];
      let othersBalance = 0n;

      for (let i = 0; i < holders.length; i++) {
        if (i < TOP_N) {
          chartData.push({
            address: holders[i].address,
            balance: Number(holders[i].balance),
            percentage: (Number(holders[i].balance) / total) * 100,
          });
        } else {
          othersBalance += BigInt(holders[i].balance);
        }
      }

      if (othersBalance > 0n) {
        chartData.push({
          address: `Others (${holders.length - TOP_N} holders)`,
          balance: Number(othersBalance),
          percentage: (Number(othersBalance) / total) * 100,
        });
      }

      if (chart) {
        chart.destroy();
      }

      if (chartCanvas) {
        chart = new Chart(chartCanvas, {
          type: "pie",
          data: {
            labels: chartData.map((d) => truncateAddress(d.address)),
            datasets: [
              {
                data: chartData.map((d) => d.balance),
                backgroundColor: CHART_COLORS.slice(0, chartData.length),
                borderColor: "rgba(26, 26, 46, 0.8)",
                borderWidth: 2,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  color: "rgba(255, 255, 255, 0.8)",
                  padding: 12,
                  font: { size: 11 },
                  boxWidth: 12,
                },
              },
              tooltip: {
                callbacks: {
                  label: (context) => {
                    const item = chartData[context.dataIndex];
                    const formattedBalance = formatSupply(item.balance, decimals);
                    return `${formattedBalance} ${tokenSymbol} (${item.percentage.toFixed(2)}%)`;
                  },
                  title: (context) => {
                    return chartData[context[0].dataIndex].address;
                  },
                },
              },
            },
          },
        });
      }

      distributionLoading = false;
    } catch (e) {
      console.error("Error loading distribution:", e);
      distributionError = e.message || "Failed to load distribution";
      distributionLoading = false;
    }
  }

  async function handleMint() {
    mintResult = null;
    mintError = null;

    const recipient = mintRecipient.trim() || myPrincipal;
    const amount = parseAmount(mintAmount, decimals);

    if (!amount) {
      mintError = "Please enter a valid amount greater than 0";
      return;
    }

    let recipientPrincipal;
    try {
      recipientPrincipal = Principal.fromText(recipient);
    } catch (e) {
      mintError = "Invalid recipient principal address";
      return;
    }

    minting = true;
    try {
      const result = await backend.mint({
        to: { owner: recipientPrincipal, subaccount: [] },
        amount: amount,
      });

      if (result.success) {
        mintResult = `Successfully minted ${mintAmount} ${tokenSymbol} to ${recipient}`;
        mintAmount = "";
        await refreshTokenInfo();
        await loadDistribution();
      } else {
        mintError = result.error?.[0] || "Mint operation failed";
      }
    } catch (e) {
      console.error("Mint error:", e);
      mintError = e.message || "Failed to mint tokens";
    } finally {
      minting = false;
    }
  }

  onMount(async () => {
    try {
      const [info, isTestMode, principal] = await Promise.all([
        backend.get_token_info(),
        backend.is_test_mode(),
        backend.get_my_principal(),
      ]);
      tokenName = info.name;
      tokenSymbol = info.symbol;
      decimals = Number(info.decimals);
      totalSupply = formatSupply(info.total_supply, decimals);
      testMode = isTestMode;
      myPrincipal = principal;
      loading = false;

      await loadDistribution();
    } catch (e) {
      console.error("Error fetching token info:", e);
      error = e.message || "Failed to load token info";
      loading = false;
    }
  });

  onDestroy(() => {
    if (chart) {
      chart.destroy();
    }
  });
</script>

<main>
  <div class="token-card">
    <h1>🪙 ICRC-1 Token</h1>
    
    {#if loading}
      <div class="loading">Loading token information...</div>
    {:else if error}
      <div class="error">{error}</div>
    {:else}
      <div class="token-info">
        <div class="info-row">
          <span class="label">Name:</span>
          <span class="value">{tokenName}</span>
        </div>
        <div class="info-row">
          <span class="label">Symbol:</span>
          <span class="value">{tokenSymbol}</span>
        </div>
        <div class="info-row">
          <span class="label">Total Supply:</span>
          <span class="value supply">{totalSupply} {tokenSymbol}</span>
        </div>
      </div>

      <div class="distribution-section">
        <h2>📊 Token Distribution</h2>
        {#if distributionLoading}
          <div class="loading">Loading distribution...</div>
        {:else if distributionError}
          <div class="error">{distributionError}</div>
        {:else if holderCount === 0}
          <div class="no-holders">No token holders yet</div>
        {:else}
          <div class="distribution-stats">
            <span class="holder-count">{holderCount} holder{holderCount !== 1 ? 's' : ''}</span>
          </div>
          <div class="chart-container">
            <canvas bind:this={chartCanvas}></canvas>
          </div>
        {/if}
      </div>

      {#if testMode}
        <div class="mint-section">
          <h2>🧪 Mint Tokens (Test Mode)</h2>
          <div class="mint-form">
            <div class="form-group">
              <label for="recipient">Recipient Principal</label>
              <input
                type="text"
                id="recipient"
                bind:value={mintRecipient}
                placeholder={myPrincipal}
                disabled={minting}
              />
              <span class="hint">Leave empty to mint to yourself</span>
            </div>
            <div class="form-group">
              <label for="amount">Amount ({tokenSymbol})</label>
              <input
                type="number"
                id="amount"
                bind:value={mintAmount}
                placeholder="0.00"
                min="0"
                step="any"
                disabled={minting}
              />
            </div>
            <button class="mint-button" on:click={handleMint} disabled={minting}>
              {minting ? "Minting..." : "Mint Tokens"}
            </button>

            {#if mintResult}
              <div class="mint-success">{mintResult}</div>
            {/if}
            {#if mintError}
              <div class="mint-error">{mintError}</div>
            {/if}
          </div>
        </div>
      {/if}
    {/if}
  </div>
</main>
