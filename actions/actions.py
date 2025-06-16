from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset


class ActionCalcularDiagnostico(Action):
    """
    Calcula el diagnóstico, lo comunica al usuario y, si el riesgo es
    moderado o alto, pregunta si desea recibir recomendaciones.
    """

    def name(self) -> Text:
        return "action_calcular_diagnostico"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # --- Esta parte de cálculo de puntuación es correcta ---
        respuestas_afirmativas = ["sí", "si", "correcto", "afirmativo", "claro", "por supuesto", "exacto"]
        slot_preocupacion = tracker.get_slot("respuesta_preocupacion") or ""
        slot_tolerancia = tracker.get_slot("respuesta_tolerancia") or ""
        slot_abstinencia = tracker.get_slot("respuesta_abstinencia") or ""
        slot_conflicto = tracker.get_slot("respuesta_conflicto") or ""

        puntuacion = 0
        if slot_preocupacion.lower() in respuestas_afirmativas: puntuacion += 1
        if slot_tolerancia.lower() in respuestas_afirmativas: puntuacion += 1
        if slot_abstinencia.lower() in respuestas_afirmativas: puntuacion += 1
        if slot_conflicto.lower() in respuestas_afirmativas: puntuacion += 1

        # --- Esta parte de enviar mensajes es correcta ---
        if puntuacion <= 1:
            dispatcher.utter_message(response="utter_diagnostico_bajo")
        elif puntuacion <= 3:
            dispatcher.utter_message(response="utter_diagnostico_moderado")
            dispatcher.utter_message(response="utter_ask_recomendaciones")
        else:  # puntuacion == 4
            dispatcher.utter_message(response="utter_diagnostico_alto")
            dispatcher.utter_message(response="utter_ask_recomendaciones")

        # --- ESTA ES LA LÍNEA CORREGIDA ---
        # En lugar de usar 'dispatcher.dispatch', devolvemos el evento
        # para que Rasa Core actualice el slot.
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

        if puntuacion and puntuacion <= 3:  # Riesgo moderado
            dispatcher.utter_message(response="utter_recomendacion_notificaciones")
            dispatcher.utter_message(response="utter_recomendacion_horarios")
            dispatcher.utter_message(response="utter_recomendacion_hobbies")
        elif puntuacion and puntuacion > 3:  # Riesgo alto
            dispatcher.utter_message(response="utter_recomendacion_notificaciones")
            dispatcher.utter_message(response="utter_recomendacion_horarios")
            dispatcher.utter_message(response="utter_recomendacion_zonas_libres")
            dispatcher.utter_message(response="utter_recomendacion_hobbies")

        dispatcher.utter_message(response="utter_diagnostico_final_ayuda")

        # Ahora que el flujo ha terminado, reseteamos todos los slots.
        return [AllSlotsReset()]