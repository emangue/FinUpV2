module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/path [external] (path, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("path", () => require("path"));

module.exports = mod;
}),
"[project]/src/app/api/transactions/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GET",
    ()=>GET
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$better$2d$sqlite3__$5b$external$5d$__$28$better$2d$sqlite3$2c$__cjs$2c$__$5b$project$5d2f$node_modules$2f$better$2d$sqlite3$29$__ = __turbopack_context__.i("[externals]/better-sqlite3 [external] (better-sqlite3, cjs, [project]/node_modules/better-sqlite3)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/path [external] (path, cjs)");
;
;
;
async function GET(request) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const type = searchParams.get('type') || 'all' // all, receitas, despesas
        ;
        const page = parseInt(searchParams.get('page') || '1');
        const limit = parseInt(searchParams.get('limit') || '10');
        const offset = (page - 1) * limit;
        // Filtros avançados
        const estabelecimento = searchParams.get('estabelecimento');
        const grupo = searchParams.get('grupo');
        const subgrupo = searchParams.get('subgrupo');
        const tipoGasto = searchParams.get('tipoGasto');
        const banco = searchParams.get('banco');
        const mesInicio = searchParams.get('mesInicio');
        const mesFim = searchParams.get('mesFim');
        const dbPath = __TURBOPACK__imported__module__$5b$externals$5d2f$path__$5b$external$5d$__$28$path$2c$__cjs$29$__["default"].join(process.cwd(), 'financas_dev.db');
        const db = new __TURBOPACK__imported__module__$5b$externals$5d2f$better$2d$sqlite3__$5b$external$5d$__$28$better$2d$sqlite3$2c$__cjs$2c$__$5b$project$5d2f$node_modules$2f$better$2d$sqlite3$29$__["default"](dbPath);
        const whereClauses = [
            'IgnorarDashboard = 0'
        ];
        const params = [];
        if (type === 'receitas') {
            whereClauses.push("TipoTransacao = ?");
            params.push('Receitas');
        } else if (type === 'despesas') {
            whereClauses.push("(TipoTransacao = ? OR TipoTransacao = ?)");
            params.push('Despesas', 'Cartão de Crédito');
        }
        if (estabelecimento) {
            whereClauses.push('Estabelecimento LIKE ?');
            params.push(`%${estabelecimento}%`);
        }
        if (grupo && grupo.trim()) {
            whereClauses.push('GRUPO = ?');
            params.push(grupo.trim());
        }
        if (subgrupo) {
            whereClauses.push('SUBGRUPO LIKE ?');
            params.push(`%${subgrupo}%`);
        }
        if (tipoGasto && tipoGasto.trim()) {
            whereClauses.push('TipoGasto = ?');
            params.push(tipoGasto.trim());
        }
        if (banco && banco.trim()) {
            whereClauses.push('banco_origem = ?');
            params.push(banco.trim());
        }
        if (mesInicio) {
            whereClauses.push('MesFatura >= ?');
            params.push(mesInicio);
        }
        if (mesFim) {
            whereClauses.push('MesFatura <= ?');
            params.push(mesFim);
        }
        const whereClause = 'WHERE ' + whereClauses.join(' AND ');
        // Buscar total de registros
        const countQuery = `SELECT COUNT(*) as total FROM journal_entries ${whereClause}`;
        const countResult = db.prepare(countQuery).get(...params);
        const total = countResult.total;
        // Buscar transações
        const query = `
      SELECT 
        IdTransacao,
        Data,
        Estabelecimento,
        ValorPositivo,
        TipoTransacao,
        GRUPO,
        SUBGRUPO,
        TipoGasto,
        origem_classificacao,
        MesFatura,
        banco_origem,
        NomeCartao
      FROM journal_entries
      ${whereClause}
      ORDER BY Data DESC
      LIMIT ? OFFSET ?
    `;
        const transactions = db.prepare(query).all(...params, limit, offset);
        db.close();
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            transactions,
            pagination: {
                page,
                limit,
                total,
                totalPages: Math.ceil(total / limit)
            }
        });
    } catch (error) {
        console.error('Erro ao buscar transações:', error);
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: 'Erro interno do servidor'
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__56377e66._.js.map