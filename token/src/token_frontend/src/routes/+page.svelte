<script>
  import "../index.scss";
  import { backend } from "$lib/canisters";
  import { Principal } from "@dfinity/principal";
  import { onMount } from "svelte";

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

  async function refreshTokenInfo() {
    const info = await backend.get_token_info();
    totalSupply = formatSupply(info.total_supply, decimals);
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
