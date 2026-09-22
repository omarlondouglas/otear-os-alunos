#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const args = process.argv.slice(2);
const command = args.find((arg) => !arg.startsWith('-')) || 'help';
const valueAfter = (flag) => { const index = args.indexOf(flag); return index >= 0 ? args[index + 1] : undefined; };
const vault = path.resolve(valueAfter('--vault') || process.cwd());
const profileName = valueAfter('--profile') || 'essencial';
const relative = (...parts) => path.join(vault, ...parts);
const exists = (...parts) => fs.existsSync(relative(...parts));
const print = (message) => process.stdout.write(`${message}\n`);
const fail = (message) => { process.stderr.write(`ERRO: ${message}\n`); process.exitCode = 1; };
const hasCommand = (name) => {
  const probe = process.platform === 'win32' ? 'where.exe' : 'command';
  const probeArgs = process.platform === 'win32' ? [name] : ['-v', name];
  return spawnSync(probe, probeArgs, { stdio: 'ignore', shell: process.platform !== 'win32' }).status === 0;
};
function readProfiles() {
  const profileFile = relative('produto-otear-os', 'perfis-dependencias.json');
  if (!fs.existsSync(profileFile)) throw new Error(`Manifesto de perfis não encontrado: ${profileFile}`);
  return JSON.parse(fs.readFileSync(profileFile, 'utf8'));
}
function help() {
  print('Otear OS — comandos locais e sem instalação automática');
  print('Uso: npx . <comando> [--profile NOME] [--vault CAMINHO]');
  print('Comandos: profiles | doctor | validate | setup');
  print('Perfis: essencial, criacao, automacao-local, infra-docker');
}
function profiles() {
  const manifest = readProfiles();
  print('Perfis de dependência (opt-in; Docker só aparece em infra-docker):');
  for (const profile of manifest.profiles) {
    print(`- ${profile.id}: ${profile.summary}`);
    print(`  Módulos: ${profile.modules.join(', ')}`);
    print(`  Dependências: ${profile.requirements.map((item) => item.name).join(', ') || 'nenhuma'}`);
  }
}
function doctor() {
  const profile = readProfiles().profiles.find((item) => item.id === profileName);
  if (!profile) return fail(`Perfil desconhecido: ${profileName}. Use \`npx . profiles\`.`);
  let problems = 0;
  print(`Diagnóstico Otear OS — perfil ${profile.id}`);
  for (const file of ['SOUL.md', 'ATIVAR-HERMES.md', 'produto-otear-os/catalogo-integracao.json']) {
    const ok = exists(...file.split('/'));
    print(`${ok ? 'OK' : 'FALTA'}  ${file}`);
    if (!ok) problems++;
  }
  for (const requirement of profile.requirements) {
    const present = requirement.command ? hasCommand(requirement.command) : true;
    print(`${present ? 'OK' : requirement.required ? 'FALTA' : 'OPCIONAL AUSENTE'}  ${requirement.name}${requirement.command ? ` (${requirement.command})` : ''}`);
    if (!present && requirement.required) problems++;
  }
  if (profile.id === 'infra-docker') print('Docker é opcional no Otear OS; este perfil só atende módulos containerizados.');
  if (problems) return fail(`${problems} requisito(s) obrigatório(s) não atendido(s) no perfil ${profile.id}.`);
  print(`OK: perfil ${profile.id} pronto para o escopo declarado.`);
}
function validate() {
  const validator = relative('produto-otear-os', 'nucleo-otear', 'scripts', 'Validar-OtearOS.ps1');
  const hermesValidator = relative('produto-otear-os', 'hermes-native', 'scripts', 'Validar-HermesNative.ps1');
  if (!fs.existsSync(validator)) return fail(`Validador não encontrado: ${validator}`);
  if (!fs.existsSync(hermesValidator)) return fail(`Validador Hermes-native não encontrado: ${hermesValidator}`);
  const shell = process.platform === 'win32' ? 'powershell.exe' : 'pwsh';
  const result = spawnSync(shell, ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', validator, '-VaultPath', vault], { stdio: 'inherit' });
  if (result.error) return fail(`Não foi possível executar PowerShell: ${result.error.message}`);
  if (result.status !== 0) return process.exitCode = result.status || 1;
  const hermesResult = spawnSync(shell, ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', hermesValidator, '-VaultPath', vault], { stdio: 'inherit' });
  if (hermesResult.error) return fail(`Não foi possível executar o validador Hermes-native: ${hermesResult.error.message}`);
  if (hermesResult.status !== 0) process.exitCode = hermesResult.status || 1;
}
function setup() {
  const profile = readProfiles().profiles.find((item) => item.id === profileName);
  if (!profile) return fail(`Perfil desconhecido: ${profileName}. Use \`npx . profiles\`.`);
  print(`Setup guiado — perfil ${profile.id}`);
  print('Nenhuma dependência será instalada por este comando.');
  for (const requirement of profile.requirements) print(`- ${requirement.name}: ${requirement.install_hint}`);
  print(`Depois, rode \`npx . doctor --profile ${profile.id}\` e \`npx . validate\`.`);
}
try { ({ help, profiles, doctor, validate, setup }[command] || help)(); } catch (error) { fail(error.message); }
