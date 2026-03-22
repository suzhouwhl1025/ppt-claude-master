/**
 * PPT Master - OpenClaw Skill 入口
 *
 * AI 驱动的多格式 SVG 内容生成系统
 * 将 PDF/URL/Markdown 转换为精美可编辑的 PowerPoint 演示文稿
 *
 * @packageDocumentation
 */

import * as path from 'path';
import { spawn } from 'child_process';

// ============================================================================
// 类型定义 - OpenClaw Context 接口
// ============================================================================

/**
 * OpenClaw Session 接口
 */
interface Session {
  send(message: string): Promise<void>;
}

/**
 * OpenClaw SessionContext 接口
 * (OpenClaw Core 在运行时提供，这里定义本地类型以避免编译错误)
 */
interface SessionContext {
  session?: Session;
  // 其他上下文属性...
  [key: string]: unknown;
}

// ============================================================================

/**
 * PPT Master 操作类型
 */
type PPTAction =
  | 'create_ppt'      // 创建完整 PPT
  | 'init_project'    // 初始化项目
  | 'import_sources'   // 导入源文件
  | 'post_process'     // 后处理
  | 'svg_to_pptx'      // SVG 转 PPTX
  | 'validate'         // 验证项目
  | 'generate_image'   // 生成图片
  | 'check_account'    // 检查账户状态
  | 'help';            // 显示帮助

/**
 * PPT 格式类型
 */
type PPTFormat = 'ppt169' | 'ppt43' | 'xhs' | 'story' | 'moments';

/**
 * 设计风格类型
 */
type PPTStyle = 'general' | 'consultant' | 'consultant_top';

/**
 * 创建 PPT 参数
 */
interface CreatePPTParams {
  action: 'create_ppt';
  source?: string;
  format?: PPTFormat;
  style?: PPTStyle;
  pages?: number;
  template?: string;
  name?: string;
}

/**
 * 初始化项目参数
 */
interface InitProjectParams {
  action: 'init_project';
  name: string;
  format?: PPTFormat;
}

/**
 * 导入源文件参数
 */
interface ImportSourcesParams {
  action: 'import_sources';
  projectPath: string;
  sources: string[];
  move?: boolean;
}

/**
 * 后处理参数
 */
interface PostProcessParams {
  action: 'post_process';
  projectPath: string;
}

/**
 * SVG 转 PPTX 参数
 */
interface SVGToPPTXParams {
  action: 'svg_to_pptx';
  projectPath: string;
  stage?: 'final' | 'output';
}

/**
 * 验证项目参数
 */
interface ValidateParams {
  action: 'validate';
  projectPath: string;
}

/**
 * 帮助参数
 */
interface HelpParams {
  action: 'help';
}

/**
 * 生成图片参数
 */
interface GenerateImageParams {
  action: 'generate_image';
  prompt: string;
  apiKey?: string;
  output?: string;
  filename?: string;
  aspectRatio?: string;
  imageSize?: string;
}

/**
 * 检查账户参数
 */
interface CheckAccountParams {
  action: 'check_account';
  apiKey?: string;
}

/**
 * 联合参数类型
 */
type PPTSkillParams =
  | CreatePPTParams
  | InitProjectParams
  | ImportSourcesParams
  | PostProcessParams
  | SVGToPPTXParams
  | ValidateParams
  | GenerateImageParams
  | CheckAccountParams
  | HelpParams;

/**
 * PPT Master 配置
 */
interface PPTMasterConfig {
  skillPath: string;
  scriptsPath: string;
  templatesPath: string;
}

// ============================================================================
// 常量定义
// ============================================================================

const SKILL_NAME = 'ppt-master';
const DEFAULT_FORMAT: PPTFormat = 'ppt169';
const DEFAULT_STYLE: PPTStyle = 'general';

const CONFIG: PPTMasterConfig = {
  skillPath: path.join(__dirname, '../assets/ppt-master-skills'),
  scriptsPath: '',
  templatesPath: ''
};

/**
 * Python 脚本路径映射
 */
const SCRIPT_MAP: Record<string, string> = {
  'project_manager': 'project_manager.py',
  'pdf_to_md': 'pdf_to_md.py',
  'web_to_md': 'web_to_md.py',
  'total_md_split': 'total_md_split.py',
  'finalize_svg': 'finalize_svg.py',
  'svg_to_pptx': 'svg_to_pptx.py',
  'svg_quality_checker': 'svg_quality_checker.py',
  'analyze_images': 'analyze_images.py',
  'runninghub_image_gen': 'runninghub_image_gen.py'
};

// ============================================================================
// 工具函数
// ============================================================================

/**
 * 获取技能根目录
 */
function getSkillRoot(): string {
  return path.join(__dirname, '..');
}

/**
 * 获取 Python 脚本完整路径
 */
function getScriptPath(scriptName: string): string {
  const skillRoot = getSkillRoot();
  // 指向原 ppt-master skills 目录
  const scriptsPath = path.join(skillRoot, 'assets', 'ppt-master-skills', 'scripts');
  const scriptFile = SCRIPT_MAP[scriptName] || `${scriptName}.py`;
  return path.join(scriptsPath, scriptFile);
}

/**
 * 运行 Python 脚本
 */
async function runPythonScript(
  scriptName: string,
  args: string[] = []
): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  const scriptPath = getScriptPath(scriptName);
  const pythonArgs = [scriptPath, ...args];

  return new Promise((resolve) => {
    const proc = spawn('python3', pythonArgs, {
      cwd: getSkillRoot(),
      shell: true
    });

    let stdout = '';
    let stderr = '';

    proc.stdout?.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr?.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      resolve({
        stdout,
        stderr,
        exitCode: code ?? 0
      });
    });

    proc.on('error', (err) => {
      stderr += err.message;
      resolve({
        stdout,
        stderr,
        exitCode: 1
      });
    });
  });
}

/**
 * 发送消息给用户
 */
async function sendMessage(ctx: SessionContext, message: string): Promise<void> {
  if (ctx.session) {
    await ctx.session.send(message);
  }
  console.log(message);
}

/**
 * 格式化输出 JSON
 */
function formatJSON(obj: unknown): string {
  return JSON.stringify(obj, null, 2);
}

// ============================================================================
// 核心功能函数
// ============================================================================

/**
 * 显示帮助信息
 */
async function showHelp(ctx: SessionContext): Promise<void> {
  const helpText = `
# PPT Master - 帮助信息

## 支持的操作

| action | 说明 | 参数 |
|--------|------|------|
| create_ppt | 创建完整 PPT | source, format, style, pages, template |
| init_project | 初始化项目 | name, format |
| import_sources | 导入源文件 | projectPath, sources, move |
| post_process | 后处理 | projectPath |
| svg_to_pptx | SVG 转 PPTX | projectPath, stage |
| validate | 验证项目 | projectPath |
| generate_image | 生成图片 | prompt, apiKey, output, aspectRatio, imageSize |
| check_account | 检查账户状态 | apiKey (可选) |

## 使用示例

\`\`\`typescript
// 创建 PPT
await main(ctx, {
  action: 'create_ppt',
  source: 'path/to/document.pdf',
  format: 'ppt169',
  style: 'consultant'
});

// 初始化项目
await main(ctx, {
  action: 'init_project',
  name: 'my-ppt',
  format: 'ppt169'
});

// 生成图片 (需要 RunningHub API Key)
await main(ctx, {
  action: 'generate_image',
  prompt: '一只在草地上奔跑的小狗',
  aspectRatio: '16:9',
  imageSize: '1K',
  output: './images'
});

// 检查账户状态
await main(ctx, {
  action: 'check_account'
});
\`\`\`

## 支持的格式

- ppt169 (默认): 16:9 演示文稿
- ppt43: 4:3 演示文稿
- xhs: 小红书笔记
- story: 短视频/抖音
- moments: 微信朋友圈

## 支持的风格

- general: 通用灵活风格
- consultant: 咨询风格
- consultant_top: 顶级咨询风格 (MBB级别)

## 图片生成 (RunningHub API)

需要 RunningHub API Key:
1. 注册: https://www.runninghub.cn
2. 获取 Key: https://www.runninghub.cn/enterprise-api/sharedApi
3. 充值: https://www.runninghub.cn/vip-rights/4

支持的图片尺寸: 512px, 1K (1024), 2K (2048), 4K (4096)
支持的宽高比: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9
`;

  await sendMessage(ctx, helpText);
}

/**
 * 显示 API Key 配置提示
 */
async function showApiKeyGuide(ctx: SessionContext): Promise<void> {
  const guide = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 未找到 RunningHub API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 请按以下步骤获取 API Key:

1️⃣ 访问 https://www.runninghub.cn 注册账户

2️⃣ 访问 https://www.runninghub.cn/enterprise-api/sharedApi
   创建 API Key

3️⃣ 访问 https://www.runninghub.cn/vip-rights/4
   充值账户（API 调用需要余额）

📝 配置方式 (三选一):

✅ 方式1: 在对话中提供 API Key
   请告诉我您的 RunningHub API Key

✅ 方式2: 设置环境变量
   export RUNNINGHUB_API_KEY='您的KEY'

✅ 方式3: 安装 runninghub skill
   它会自动配置 API Key

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
  await sendMessage(ctx, guide);
}

/**
 * 检查账户状态
 */
async function checkAccount(
  ctx: SessionContext,
  apiKey?: string
): Promise<{ success: boolean; error?: string }> {
  await sendMessage(ctx, `🔍 检查账户状态...`);

  const args = ['--check'];
  if (apiKey) {
    args.push('--api_key', apiKey);
  }

  const result = await runPythonScript('runninghub_image_gen', args);

  if (result.exitCode === 0) {
    await sendMessage(ctx, `✅ 账户状态检查成功\n${result.stdout}`);
    return { success: true };
  } else {
    const errorMsg = result.stderr || result.stdout;
    if (errorMsg.includes('NO_API_KEY') || errorMsg.includes('未找到')) {
      await showApiKeyGuide(ctx);
    } else {
      await sendMessage(ctx, `❌ 账户检查失败: ${errorMsg}`);
    }
    return { success: false, error: errorMsg };
  }
}

/**
 * 生成图片
 */
async function generateImage(
  ctx: SessionContext,
  params: GenerateImageParams
): Promise<{ success: boolean; outputPath?: string; error?: string }> {
  const {
    prompt,
    apiKey,
    output,
    filename,
    aspectRatio = '16:9',
    imageSize = '1K'
  } = params;

  // 先检查 API Key
  if (!apiKey) {
    // 尝试检查是否有可用的 API Key
    const checkResult = await checkAccount(ctx, undefined);
    if (!checkResult.success) {
      // API Key 不可用，引导用户配置
      return {
        success: false,
        error: '需要 RunningHub API Key 才能生成图片'
      };
    }
  }

  await sendMessage(ctx, `🎨 开始生成图片...`);
  await sendMessage(ctx, `📝 提示词: ${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}`);

  const args: string[] = [prompt];

  if (output) {
    args.push('--output', output);
  }
  if (filename) {
    args.push('--filename', filename);
  }
  args.push('--aspect_ratio', aspectRatio);
  args.push('--image_size', imageSize);

  if (apiKey) {
    args.push('--api_key', apiKey);
  }

  const result = await runPythonScript('runninghub_image_gen', args);

  if (result.exitCode === 0) {
    const outputPath = result.stdout.match(/图片路径: (.+)/)?.[1] ||
                       result.stdout.match(/File saved to: (.+)/)?.[1] ||
                       output || 'images/';
    await sendMessage(ctx, `✅ 图片生成成功!\n${result.stdout}`);
    return { success: true, outputPath };
  } else {
    const errorMsg = result.stderr || result.stdout;
    if (errorMsg.includes('NO_API_KEY') || errorMsg.includes('未找到')) {
      await showApiKeyGuide(ctx);
    } else {
      await sendMessage(ctx, `❌ 图片生成失败: ${errorMsg}`);
    }
    return { success: false, error: errorMsg };
  }
}

/**
 * 初始化项目
 */
async function initProject(
  ctx: SessionContext,
  name: string,
  format: PPTFormat = DEFAULT_FORMAT
): Promise<{ success: boolean; projectPath?: string; error?: string }> {
  await sendMessage(ctx, `📁 初始化项目: ${name} (格式: ${format})`);

  const result = await runPythonScript('project_manager', [
    'init',
    name,
    '--format',
    format
  ]);

  if (result.exitCode === 0) {
    const projectPath = path.join(getSkillRoot(), 'projects', name);
    await sendMessage(ctx, `✅ 项目初始化成功: ${projectPath}`);
    return { success: true, projectPath };
  } else {
    await sendMessage(ctx, `❌ 项目初始化失败: ${result.stderr}`);
    return { success: false, error: result.stderr };
  }
}

/**
 * 导入源文件
 */
async function importSources(
  ctx: SessionContext,
  projectPath: string,
  sources: string[],
  move: boolean = true
): Promise<{ success: boolean; error?: string }> {
  await sendMessage(ctx, `📥 导入源文件到: ${projectPath}`);

  const args = ['import-sources', projectPath, ...sources];
  if (move) {
    args.push('--move');
  }

  const result = await runPythonScript('project_manager', args);

  if (result.exitCode === 0) {
    await sendMessage(ctx, `✅ 源文件导入成功`);
    return { success: true };
  } else {
    await sendMessage(ctx, `❌ 源文件导入失败: ${result.stderr}`);
    return { success: false, error: result.stderr };
  }
}

/**
 * 后处理 - 执行 total_md_split.py -> finalize_svg.py -> svg_to_pptx.py
 */
async function postProcess(
  ctx: SessionContext,
  projectPath: string
): Promise<{ success: boolean; outputPath?: string; error?: string }> {
  await sendMessage(ctx, `🔄 开始后处理...`);

  // Step 1: total_md_split.py
  await sendMessage(ctx, `📝 Step 1/3: 分割演讲稿...`);
  let result = await runPythonScript('total_md_split', [projectPath]);
  if (result.exitCode !== 0) {
    await sendMessage(ctx, `❌ 分割演讲稿失败: ${result.stderr}`);
    return { success: false, error: result.stderr };
  }

  // Step 2: finalize_svg.py
  await sendMessage(ctx, `🎨 Step 2/3: SVG 后处理...`);
  result = await runPythonScript('finalize_svg', [projectPath]);
  if (result.exitCode !== 0) {
    await sendMessage(ctx, `❌ SVG 后处理失败: ${result.stderr}`);
    return { success: false, error: result.stderr };
  }

  // Step 3: svg_to_pptx.py
  await sendMessage(ctx, `📊 Step 3/3: 导出 PPTX...`);
  result = await runPythonScript('svg_to_pptx', [projectPath, '-s', 'final']);
  if (result.exitCode !== 0) {
    await sendMessage(ctx, `❌ PPTX 导出失败: ${result.stderr}`);
    return { success: false, error: result.stderr };
  }

  const outputPath = path.join(projectPath, 'output.pptx');
  await sendMessage(ctx, `✅ 后处理完成! 输出: ${outputPath}`);
  return { success: true, outputPath };
}

/**
 * SVG 转 PPTX
 */
async function svgToPPTX(
  ctx: SessionContext,
  projectPath: string,
  stage: 'final' | 'output' = 'final'
): Promise<{ success: boolean; outputPath?: string; error?: string }> {
  await sendMessage(ctx, `📊 导出 PPTX (stage: ${stage})...`);

  const result = await runPythonScript('svg_to_pptx', [
    projectPath,
    '-s',
    stage
  ]);

  if (result.exitCode === 0) {
    const outputPath = path.join(projectPath, `${stage}.pptx`);
    await sendMessage(ctx, `✅ PPTX 导出成功: ${outputPath}`);
    return { success: true, outputPath };
  } else {
    await sendMessage(ctx, `❌ PPTX 导出失败: ${result.stderr}`);
    return { success: false, error: result.stderr };
  }
}

/**
 * 验证项目
 */
async function validateProject(
  ctx: SessionContext,
  projectPath: string
): Promise<{ success: boolean; errors?: string[] }> {
  await sendMessage(ctx, `🔍 验证项目: ${projectPath}`);

  const result = await runPythonScript('project_manager', [
    'validate',
    projectPath
  ]);

  if (result.exitCode === 0) {
    await sendMessage(ctx, `✅ 项目验证通过`);
    return { success: true };
  } else {
    await sendMessage(ctx, `❌ 项目验证失败: ${result.stderr}`);
    return { success: false, errors: result.stderr.split('\n') };
  }
}

/**
 * 创建完整 PPT
 */
async function createPPT(
  ctx: SessionContext,
  params: CreatePPTParams
): Promise<{ success: boolean; outputPath?: string; error?: string }> {
  const {
    source,
    format = DEFAULT_FORMAT,
    style = DEFAULT_STYLE,
    name
  } = params;

  await sendMessage(ctx, `
🚀 开始创建 PPT
━━━━━━━━━━━━━━━━━━━━
📄 源文件: ${source || '未指定'}
📐 格式: ${format}
🎨 风格: ${style}
━━━━━━━━━━━━━━━━━━━━
`);

  // 如果有源文件，先导入
  if (source) {
    const projectName = name || `ppt_${Date.now()}`;

    // 初始化项目
    const initResult = await initProject(ctx, projectName, format);
    if (!initResult.success) {
      return { success: false, error: initResult.error };
    }

    // 导入源文件
    const projectPath = initResult.projectPath!;
    const importResult = await importSources(ctx, projectPath, [source]);
    if (!importResult.success) {
      return { success: false, error: importResult.error };
    }

    // 执行后处理
    const postResult = await postProcess(ctx, projectPath);
    return postResult;
  } else {
    // 仅初始化项目
    const projectName = name || `ppt_${Date.now()}`;
    const initResult = await initProject(ctx, projectName, format);
    return initResult;
  }
}

// ============================================================================
// 主入口函数
// ============================================================================

/**
 * PPT Master Skill 主入口
 */
export async function main(
  ctx: SessionContext,
  params: PPTSkillParams
): Promise<unknown> {
  const { action } = params;

  console.log(`[${SKILL_NAME}] 收到请求: action=${action}`);

  switch (action) {
    case 'help':
      await showHelp(ctx);
      return { success: true };

    case 'create_ppt':
      return await createPPT(ctx, params as CreatePPTParams);

    case 'init_project':
      return await initProject(
        ctx,
        (params as InitProjectParams).name,
        (params as InitProjectParams).format
      );

    case 'import_sources':
      return await importSources(
        ctx,
        (params as ImportSourcesParams).projectPath,
        (params as ImportSourcesParams).sources,
        (params as ImportSourcesParams).move
      );

    case 'post_process':
      return await postProcess(ctx, (params as PostProcessParams).projectPath);

    case 'svg_to_pptx':
      return await svgToPPTX(
        ctx,
        (params as SVGToPPTXParams).projectPath,
        (params as SVGToPPTXParams).stage
      );

    case 'validate':
      return await validateProject(ctx, (params as ValidateParams).projectPath);

    case 'generate_image':
      return await generateImage(ctx, params as GenerateImageParams);

    case 'check_account':
      return await checkAccount(ctx, (params as CheckAccountParams).apiKey);

    default:
      await sendMessage(ctx, `❌ 未知操作: ${action}`);
      return { success: false, error: `Unknown action: ${action}` };
  }
}

// ============================================================================
// 导出默认函数
// ============================================================================

export default main;
