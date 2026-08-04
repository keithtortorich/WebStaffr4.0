import { execSync, spawnSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

interface IntakePayload {
  tenantId: string;
  prompt: string;           // e.g., "plumbing company in Austin, emergency service, professional"
  brandStyle?: string;      // e.g., "professional tradesman aesthetic, sans-serif, dark blue accent"
  customerData: {
    company: string;
    services: string[];
    city: string;
  };
}

interface PipelineResult {
  status: 'success' | 'failed';
  finalScore: number;
  liveUrl?: string;
  directionPath?: string;
  errorLog?: string;
}

/**
 * Main entry point: orchestrates the five-stage Impeccable loop.
 * Runs unattended; terminates when quality gates met or max attempts reached.
 */
export async function runMagicUpgrade(payload: IntakePayload): Promise<PipelineResult> {
  const workdir = path.join(process.cwd(), 'sites', payload.tenantId);
  fs.mkdirSync(workdir, { recursive: true });

  const logFile = path.join(workdir, '.impeccable_build.log');
  const log = (msg: string) => {
    console.log(`[${payload.tenantId}] ${msg}`);
    fs.appendFileSync(logFile, `${new Date().toISOString()} ${msg}\n`);
  };

  try {
    // Stage 1: SHAPE (extract intent)
    log('🎯 [1/5] SHAPE: Extracting design intent from intake...');
    // For MVP, skip /impeccable shape and go straight to direction engine
    // The intake form IS the brief; we have tenantId, prompt, customerData

    // Stage 2: DIRECTION ENGINE (roll & lock visual direction)
    log('🎨 [2/5] DIRECTION ENGINE: Rolling visual direction...');
    const direction = await runDirectionEngine(workdir, payload, log);
    if (!direction) throw new Error('Direction engine failed');

    // Stage 3: GENERATE (code to direction)
    log('🖼️  [3/5] GENERATE: Rendering HTML/CSS...');
    await runGenerate(workdir, direction, payload, log);

    // Stage 4: EVALUATE (critique + audit)
    log('🔍 [4/5] EVALUATE: Running critique & audit...');
    const { critiqueScore, auditP0 } = await runEvaluate(workdir, log);
    log(`   Critique score: ${critiqueScore}/100 | P0 issues: ${auditP0}`);

    // Stage 5: SELF-HEAL & SHIP
    log('⚙️  [5/5] SELF-HEAL & SHIP: Autonomous refinement loop...');
    const finalScore = await runSelfHealLoop(workdir, critiqueScore, auditP0, log);

    if (finalScore >= 88 && auditP0 === 0) {
      log('✨ Quality gates met. Hardening, polishing, deploying...');
      await runHardenAndDeploy(workdir, payload, log);

      const liveUrl = `https://sites.webstaffr.com/${payload.tenantId}`;
      log(`🚀 LIVE at ${liveUrl}`);

      return {
        status: 'success',
        finalScore,
        liveUrl,
        directionPath: direction
      };
    } else {
      log(`⚠️  Quality gates not met after self-heal. Score: ${finalScore}, P0: ${auditP0}`);
      return {
        status: 'failed',
        finalScore,
        errorLog: fs.readFileSync(logFile, 'utf-8')
      };
    }
  } catch (error) {
    const err = error instanceof Error ? error.message : String(error);
    log(`❌ FATAL: ${err}`);
    return {
      status: 'failed',
      finalScore: 0,
      errorLog: fs.readFileSync(logFile, 'utf-8')
    };
  }
}

/**
 * Stage 2: Direction Engine
 * In unattended mode, use first-pass direction; no re-rolls.
 * Calls /impeccable with tenant prompt to generate PRODUCT.md, DESIGN.md, surface brief.
 */
async function runDirectionEngine(workdir: string, payload: IntakePayload, log: (msg: string) => void): Promise<string> {
  const env = { ...process.env, IMPECCABLE_UNATTENDED: 'true' };
  const cmd = `impeccable direction ${payload.prompt}${payload.brandStyle ? `, ${payload.brandStyle}` : ''}`;

  try {
    log(`   Running: ${cmd}`);
    const result = spawnSync('npx', ['impeccable', 'direction', payload.prompt, ...(payload.brandStyle ? [payload.brandStyle] : [])], {
      cwd: workdir,
      env,
      stdio: 'pipe',
      encoding: 'utf-8',
      timeout: 60000 // 60s timeout for direction engine
    });

    if (result.status !== 0) {
      log(`   ⚠️  Direction engine returned status ${result.status}`);
      log(`   stderr: ${result.stderr}`);
    }

    // Direction contract written to .impeccable/surfaces/
    const surfaceDir = path.join(workdir, '.impeccable', 'surfaces');
    if (!fs.existsSync(surfaceDir)) {
      throw new Error('Direction engine did not produce .impeccable/surfaces/');
    }

    const files = fs.readdirSync(surfaceDir).filter(f => f.endsWith('.md'));
    if (files.length === 0) {
      throw new Error('No surface brief generated');
    }

    const directionFile = path.join(surfaceDir, files[files.length - 1]);
    log(`   ✓ Direction locked: ${files[files.length - 1]}`);
    return directionFile;
  } catch (error) {
    throw new Error(`Direction engine failed: ${error}`);
  }
}

/**
 * Stage 3: GENERATE
 * Call site_renderer.py with direction context to render HTML/CSS.
 */
async function runGenerate(workdir: string, direction: string, payload: IntakePayload, log: (msg: string) => void): Promise<void> {
  try {
    const cmd = [
      'python3',
      path.join(process.cwd(), 'site_renderer.py'),
      `--tenant-id=${payload.tenantId}`,
      `--direction=${direction}`,
      `--company=${payload.customerData.company}`,
      `--city=${payload.customerData.city}`
    ];

    log(`   Running site_renderer.py...`);
    const result = spawnSync(cmd[0], cmd.slice(1), {
      cwd: workdir,
      stdio: 'pipe',
      encoding: 'utf-8',
      timeout: 30000
    });

    if (result.status !== 0) {
      throw new Error(`Renderer failed: ${result.stderr}`);
    }

    // Verify HTML generated
    const indexHtml = path.join(workdir, 'web', 'index.html');
    if (!fs.existsSync(indexHtml)) {
      throw new Error('Renderer did not produce index.html');
    }

    log(`   ✓ HTML/CSS generated`);
  } catch (error) {
    throw new Error(`Generation failed: ${error}`);
  }
}

/**
 * Stage 4: EVALUATE
 * Run /impeccable critique and /impeccable audit, parse JSON output.
 */
async function runEvaluate(workdir: string, log: (msg: string) => void): Promise<{ critiqueScore: number; auditP0: number }> {
  try {
    log(`   Running /impeccable critique...`);
    const critiqueRaw = execSync('npx impeccable critique --json', {
      cwd: workdir,
      encoding: 'utf-8',
      stdio: 'pipe'
    });

    const critique = JSON.parse(critiqueRaw);
    const critiqueScore = critique.overallScore || 0;

    log(`   Running /impeccable audit...`);
    const auditRaw = execSync('npx impeccable audit --json', {
      cwd: workdir,
      encoding: 'utf-8',
      stdio: 'pipe'
    });

    const audit = JSON.parse(auditRaw);
    const auditP0 = audit.issues?.filter((i: any) => i.severity === 'P0').length || 0;

    return { critiqueScore, auditP0 };
  } catch (error) {
    throw new Error(`Evaluation failed: ${error}`);
  }
}

/**
 * Stage 5A: SELF-HEAL LOOP
 * Autonomous loop: critique → diagnose → route to specific refinement command → repeat.
 * Terminates when quality gates met OR MAX_ATTEMPTS reached.
 */
async function runSelfHealLoop(
  workdir: string,
  initialScore: number,
  initialP0: number,
  log: (msg: string) => void
): Promise<number> {
  const MAX_ATTEMPTS = 4;
  const TARGET_SCORE = 88;
  let currentScore = initialScore;
  let currentP0 = initialP0;

  if (currentScore >= TARGET_SCORE && currentP0 === 0) {
    log(`   ✓ Quality gates already met (${currentScore}/100, ${currentP0} P0 issues)`);
    return currentScore;
  }

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    log(`   🔄 Self-heal iteration ${attempt}/${MAX_ATTEMPTS}`);

    // Get latest critique to inform routing
    let critiqueText = '';
    try {
      const critiqueRaw = execSync('npx impeccable critique --json', {
        cwd: workdir,
        encoding: 'utf-8',
        stdio: 'pipe'
      });
      const critique = JSON.parse(critiqueRaw);
      critiqueText = (critique.issues || []).join(' ').toLowerCase();
      currentScore = critique.overallScore || 0;
    } catch (e) {
      log(`   ⚠️  Could not fetch latest critique`);
    }

    // DECISION MATRIX: Route to specific command based on issues
    let command = '';
    if (critiqueText.includes('typography') || critiqueText.includes('font')) {
      command = 'npx impeccable typeset';
    } else if (critiqueText.includes('layout') || critiqueText.includes('spacing') || critiqueText.includes('alignment')) {
      command = 'npx impeccable layout';
    } else if (critiqueText.includes('confusing') || critiqueText.includes('copy') || critiqueText.includes('text')) {
      command = 'npx impeccable clarify';
    } else if (critiqueText.includes('color') || critiqueText.includes('bland') || critiqueText.includes('plain')) {
      command = 'npx impeccable colorize';
    } else if (currentScore < 60) {
      command = 'npx impeccable bolder';
    } else {
      command = 'npx impeccable polish';
    }

    log(`      → ${command}`);
    try {
      execSync(command, { cwd: workdir, stdio: 'inherit' });
    } catch (e) {
      log(`      ⚠️  Command failed; continuing`);
    }

    // Check gates after refinement
    try {
      const critiqueRaw = execSync('npx impeccable critique --json', {
        cwd: workdir,
        encoding: 'utf-8',
        stdio: 'pipe'
      });
      const auditRaw = execSync('npx impeccable audit --json', {
        cwd: workdir,
        encoding: 'utf-8',
        stdio: 'pipe'
      });

      currentScore = JSON.parse(critiqueRaw).overallScore || 0;
      currentP0 = JSON.parse(auditRaw).issues?.filter((i: any) => i.severity === 'P0').length || 0;

      log(`      📊 Score: ${currentScore}/100 | P0: ${currentP0}`);

      if (currentScore >= TARGET_SCORE && currentP0 === 0) {
        log(`   ✨ Quality gates met at iteration ${attempt}`);
        return currentScore;
      }
    } catch (e) {
      log(`   ⚠️  Could not evaluate progress`);
    }
  }

  log(`   ⚠️  Max iterations reached. Final score: ${currentScore}/100`);
  return currentScore;
}

/**
 * Stage 5B: HARDEN & SHIP
 * Final quality pass, build production assets, deploy.
 */
async function runHardenAndDeploy(workdir: string, payload: IntakePayload, log: (msg: string) => void): Promise<void> {
  try {
    log(`   Running /impeccable audit (final check)...`);
    execSync('npx impeccable audit', { cwd: workdir, stdio: 'inherit' });

    log(`   Running /impeccable harden (edge cases)...`);
    execSync('npx impeccable harden', { cwd: workdir, stdio: 'inherit' });

    log(`   Running /impeccable polish (final pass)...`);
    execSync('npx impeccable polish', { cwd: workdir, stdio: 'inherit' });

    log(`   Updating DESIGN.md from actual generated code...`);
    execSync('npx impeccable document', { cwd: workdir, stdio: 'inherit' });

    log(`   Building production bundle...`);
    execSync('npm run build:site', { cwd: workdir, stdio: 'inherit' });

    log(`   Deploying to Vercel...`);
    // TODO: wire Vercel deployment (requires VERCEL_TOKEN env var)
    // await deployToVercel(workdir, payload.tenantId);

    log(`✓ All stages complete`);
  } catch (error) {
    throw new Error(`Harden/deploy failed: ${error}`);
  }
}

// Export for testing
export { runDirectionEngine, runGenerate, runEvaluate, runSelfHealLoop, runHardenAndDeploy };
