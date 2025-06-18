from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset


class ActionCalcularDiagnostico(Action):
    def name(self) -> Text:
        return "action_calcular_diagnostico"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        respuestas_afirmativas = ["sí", "si", "correcto", "afirmativo", "claro", "por supuesto", "exacto"]

        # Obtenemos los 10 slots
        slots_a_evaluar = [
            "respuesta_preocupacion", "respuesta_tolerancia", "respuesta_abstinencia",
            "respuesta_conflicto", "respuesta_escape", "respuesta_perdida_interes",
            "respuesta_engano", "respuesta_riesgo", "respuesta_comparacion", "respuesta_uso_inmediato"
        ]

        puntuacion = 0
        for slot_name in slots_a_evaluar:
            valor_slot = tracker.get_slot(slot_name) or ""
            if valor_slot.lower() in respuestas_afirmativas:
                puntuacion += 1

        # Lógica de diagnóstico según los 5 niveles de tu presentación
        if puntuacion == 0:
            dispatcher.utter_message(response="utter_diagnostico_sin_adiccion")
        elif 1 <= puntuacion <= 3:
            dispatcher.utter_message(response="utter_diagnostico_bajo")
            dispatcher.utter_message(response="utter_ask_recomendaciones")
        elif 4 <= puntuacion <= 6:
            dispatcher.utter_message(response="utter_diagnostico_medio")
            dispatcher.utter_message(response="utter_ask_recomendaciones")
        elif 7 <= puntuacion <= 9:
            dispatcher.utter_message(response="utter_diagnostico_alto")
            dispatcher.utter_message(response="utter_ask_recomendaciones")
        else:  # puntuacion == 10
            dispatcher.utter_message(response="utter_diagnostico_muy_alto")
            dispatcher.utter_message(response="utter_ask_recomendaciones")

        return [SlotSet("puntuacion_diagnostico", float(puntuacion))]


class ActionDarRecomendaciones(Action):
    """
    Envía la lista de recomendaciones basadas en la puntuación guardada en el slot.
    """

    def name(self) -> Text:
        return "action_dar_recomendaciones"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recupera la puntuación del slot
        puntuacion = tracker.get_slot("puntuacion_diagnostico")

        dispatcher.utter_message(response="utter_recomendaciones_generales")

        if puntuacion and 4 <= puntuacion <= 6:  # Riesgo moderado
            dispatcher.utter_message(response="utter_recomendacion_notificaciones")
            dispatcher.utter_message(response="utter_recomendacion_hobbies")
        elif puntuacion and 7 <= puntuacion <= 9:  # Riesgo alto
            dispatcher.utter_message(response="utter_recomendacion_notificaciones")
            dispatcher.utter_message(response="utter_recomendacion_horarios")
            dispatcher.utter_message(response="utter_recomendacion_hobbies")
        elif puntuacion and puntuacion == 10:
            dispatcher.utter_message(response="utter_recomendacion_zonas_libres")
            dispatcher.utter_message(response="utter_recomendacion_notificaciones")
            dispatcher.utter_message(response="utter_recomendacion_horarios")
            dispatcher.utter_message(response="utter_recomendacion_hobbies")

        dispatcher.utter_message(response="utter_diagnostico_final_ayuda")

        # Ahora que el flujo ha terminado, reseteamos todos los slots.
        return [AllSlotsReset()]