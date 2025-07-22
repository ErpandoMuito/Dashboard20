#!/usr/bin/env python3
"""
Script para popular o cache com todos os produtos PH
"""
import asyncio
import httpx
from typing import Dict

# Lista completa de produtos PH com seus IDs
PRODUTOS_PH = {
    "913575755": "PH-90",
    "913575779": "PH-80",
    "913018453": "PH-471",
    "913018510": "PH-470",
    "913199477": "PH-473",
    "913199481": "PH-474",
    "910424889": "PH-810",
    "913567024": "PH-100",
    "913295929": "PH-952",
    "900686547": "PH-420",
    "900686569": "PH-430",
    "892410784": "PH-200",
    "893914022": "PH-210",
    "897245184": "PH-710",
    "912907830": "PH-950",
    "912907833": "PH-951",
    "892454990": "PH-920",
    "892461370": "PH-930",
    "892670115": "PH-30",
    "894031521": "PH-40",
    "892412735": "PH-900",
    "892411801": "PH-910",
    "913018308": "PH-476",
    "913018277": "PH-478",
    "892658665": "PH-20",
    "892671020": "PH-50",
    "892672334": "PH-10",
    "913671486": "PH-70",
    "893812724": "PH-300",
    "906020793": "PH-310",
    "900162481": "PH-700",
    "892407322": "PH-150",
    "892466107": "PH-400",
    "910034288": "PH-1020",
    "893437963": "PH-518",
    "893438579": "PH-519",
    "893439680": "PH-521",
    "893440221": "PH-522",
    "892475059": "PH-508",
    "899801003": "PH-523",
    "892474726": "PH-507",
    "892475364": "PH-509",
    "893434458": "PH-510",
    "892475739": "PH-511",
    "892476956": "PH-512",
    "892485576": "PH-513",
    "892485145": "PH-514",
    "898391526": "PH-524",
    "892486013": "PH-515",
    "892486392": "PH-516",
    "893436191": "PH-525",
    "893436379": "PH-526",
    "893437386": "PH-527",
    "893436619": "PH-528",
    "900162489": "PH-529",
    "892472143": "PH-505",
    "892474558": "PH-506",
    "894169723": "PH-517",
    "892469141": "PH-410",
    "892469449": "PH-500",
    "913368987": "PH-954",
    "913368979": "PH-953",
    "913062633": "PH-472",
    "897421414": "PH-60",
    "910424704": "PH-820",
    "912672853": "PH-650",
    "912506867": "PH-660",
    "912479888": "PH-670",
    "899231794": "PH-640",
    "892479348": "PH-610",
    "892481827": "PH-620",
    "892484645": "PH-630",
    "892469876": "PH-501",
    "892470129": "PH-502",
    "892471080": "PH-503",
    "892471503": "PH-504"
}

async def popular_cache():
    """Popula o cache com todos os produtos PH"""
    async with httpx.AsyncClient() as client:
        try:
            # Primeiro limpar o cache existente
            print("🧹 Limpando cache existente...")
            response = await client.post("https://dashboard-estoque-v2.fly.dev/api/v2/estoque/limpar-cache")
            print(f"Cache limpo: {response.status_code}")
            
            # Agora enviar todos os produtos
            print(f"\n📦 Enviando {len(PRODUTOS_PH)} produtos para o cache...")
            
            produtos_data = []
            for produto_id, codigo in PRODUTOS_PH.items():
                produtos_data.append({
                    "id": produto_id,
                    "codigo": codigo
                })
            
            response = await client.post(
                "https://dashboard-estoque-v2.fly.dev/api/v2/estoque/popular-cache-bulk",
                json={"produtos": produtos_data}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Cache populado com sucesso!")
                print(f"   - Total: {result['total']} produtos")
                print(f"   - Sucesso: {result['sucesso']} produtos")
                if result['falhas'] > 0:
                    print(f"   - Falhas: {result['falhas']} produtos")
            else:
                print(f"❌ Erro ao popular cache: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(popular_cache())