<script>
  import "../index.scss";
  import { backend } from "$lib/canisters";
  import { onMount } from "svelte";

  let tokenName = "Loading...";
  let tokenSymbol = "";
  let totalSupply = "Loading...";
  let decimals = 8;
  let loading = true;
  let error = null;

  function formatSupply(supply, dec) {
    const value = Number(supply) / Math.pow(10, dec);
    return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }

  onMount(async () => {
    try {
      const info = await backend.get_token_info();
      tokenName = info.name;
      tokenSymbol = info.symbol;
      decimals = Number(info.decimals);
      totalSupply = formatSupply(info.total_supply, decimals);
      loading = false;
    } catch (e) {
      console.error("Error fetching token info:", e);
      error = e.message || "Failed to load token info";
      loading = false;
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
    {/if}
  </div>
</main>
